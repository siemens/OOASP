# Copyright (c) 2024 Siemens AG Oesterreich
# SPDX-License-Identifier: MIT

from copy import deepcopy
from types import SimpleNamespace
from typing import List

from clingo import Function, Model, parse_term
from clingraph.clingo_utils import ClingraphContext
from clingraph.graphviz import compute_graphs, render
from clingraph.orm import Factbase
from clorm import (
    ConstantField,
    FactBase,
    IntegerField,
    Predicate,
    Raw,
    RawField,
    StringField,
    Symbol,
    unify,
)
from clorm.clingo import Control

import ooasp.settings as settings
import ooasp.utils as utils

from .kb import OOASPKnowledgeBase


class OOASPConfiguration:
    """
    An OOASP Configuration
    Properties:
            kb (OOASPKnowledgeBase): The Knowledge base
            name (str): The name of the configuration
            fb (clorm.Factbase): A fact base with the configuration
            UNIFIERS (Namespace): All clorm unifiers (classes) used to link objects with predicates
    """

    def __init__(self, name: str, kb: OOASPKnowledgeBase):
        """
        Creates a possibly partial configuration
            Parameters:
                config: The name of the configuration
                kb: The Knowledge base
        """
        self.name: str = name
        self.kb = kb
        self.set_unifiers()
        self.fb = FactBase()

    def __deepcopy__(self, memo):
        """
        Makes a deep copy of the configuration
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))

        return result

    def set_unifiers(self):
        """
        Sets the clorm Unifiers based on the name to filter out any other predicates in the program.
        """

        class ConfigObject(Predicate):
            class Meta:
                name = "ooasp_configobject"

            class_name = ConstantField
            object_id = IntegerField

        class Leaf(Predicate):
            class Meta:
                name = "ooasp_isa_leaf"

            class_name = ConstantField
            object_id = IntegerField

        class ObjectSmallest(Predicate):
            class Meta:
                name = "ooasp_isa_smallest"

            class_name = ConstantField
            object_id = IntegerField

        class Object(Predicate):
            class Meta:
                name = "ooasp_isa"

            class_name = ConstantField
            object_id = IntegerField

        class AttributeValue(Predicate):
            class Meta:
                name = "ooasp_attr_value"

            attr_name = ConstantField
            object_id = IntegerField
            attr_value = RawField

        class AttributeInt(Predicate):
            class Meta:
                name = "ooasp_attr_int"

            object_id = IntegerField
            attr_name = ConstantField
            min = IntegerField
            max = IntegerField

        class Association(Predicate):
            class Meta:
                name = "ooasp_associated"

            assoc_name = ConstantField
            object_id1 = IntegerField
            object_id2 = IntegerField

        class Domain(Predicate):
            class Meta:
                name = "ooasp_domain"

            class_name = ConstantField
            object_id = IntegerField

        class CV(Predicate):
            class Meta:
                name = "ooasp_cv"

            name = ConstantField
            object_id = IntegerField
            info = StringField
            args = RawField

        class User(Predicate):
            class Meta:
                name = "user"

            predicate = RawField

        self.UNIFIERS = SimpleNamespace(
            AttributeValue=AttributeValue,
            AttributeInt=AttributeInt,
            Association=Association,
            Leaf=Leaf,
            ObjectSmallest=ObjectSmallest,
            ConfigObject=ConfigObject,
            Domain=Domain,
            CV=CV,
            User=User,
            Object=Object,
        )

    @classmethod
    def from_model(cls, name: str, kb: OOASPKnowledgeBase, model: Model):
        """
        Creates a configuration from a clingo model
            Parameters:
                name: The name of the configuration
                kb: The knowledge base
                model: The clingo model
        """
        config = cls(name=name, kb=kb)
        config.fb = model.facts(
            unifier=config.unifiers_list, atoms=True, shown=True, theory=True
        )
        return config

    @property
    def unifiers_list(self) -> List:
        """
        The list of all unifiers classes
        """
        return self.UNIFIERS.__dict__.values()

    @property
    def domain_size(self) -> int:
        """
        The domain size, it is computed by counting the number of objects in the fact base.
        """
        return (
            self.fb.query(self.UNIFIERS.Domain)
            .select(self.UNIFIERS.Domain.object_id)
            .count()
        )

    @property
    def size(self) -> int:
        """
        The number of instantiated objects via isa_leaf
        """
        return (
            self.fb.query(self.UNIFIERS.Leaf)
            .select(self.UNIFIERS.Leaf.object_id)
            .count()
        )

    @property
    def has_cv(self) -> bool:
        """
        True if the configuration has any constraint violations, false otherwise
        """
        return len(self.constraint_violations) != 0

    @property
    def editable_unifiers(self) -> List:
        """
        List of all unifier classes that are editable: Object,AttributeValue,Association
        """
        return [
            self.UNIFIERS.Object,
            self.UNIFIERS.AttributeValue,
            self.UNIFIERS.Association,
        ]

    @property
    def editable_facts(self) -> List[Predicate]:
        """
        The list of all facts in the fact base that are editable.
        Editable facts are object class, attribute value and associations.
        """
        return self.associations + self.objects + self.attribute_values

    @property
    def assumptions(self) -> List[Symbol]:
        """
        The symbols for all editable facts in the configuration
        """
        return [f.symbol for f in self.editable_facts]

    @property
    def associations(self) -> List[Predicate]:
        """
        The list of associations
        """
        return list(self.fb.query(self.UNIFIERS.Association).all())

    @property
    def leafs(self) -> List[Predicate]:
        """
        The list of leafs
        """
        return list(self.fb.query(self.UNIFIERS.Leaf).all())

    @property
    def small_objects(self) -> List[Predicate]:
        """
        All the objects but only considering their most specific instantiated class.
        It can be used to get only one ooasp_isa for each object.

        For example, if an object is of type Object and Rack this will only return the Rack
        """
        return list(self.fb.query(self.UNIFIERS.ObjectSmallest).all())

    @property
    def smart_objects(self) -> List[Predicate]:
        """
        A list of objects of type self.UNIFIERS.Object such that only one instance for each object appears.
        Internally uses the small_objects method and maps them into the Objects class

        Returns:
            A list of unique objects of type self.UNIFIERS.Object with their most specific instantiated class
        """

        small_objects = {o.object_id: o.class_name for o in self.small_objects}
        objects = []
        for o in self.objects:
            if (
                o.object_id in small_objects
                and small_objects[o.object_id] != o.class_name
            ):
                continue
            objects.append(o)

        return objects

    @property
    def objects(self) -> List[Predicate]:
        """
        The list of all objects
        """
        return list(self.fb.query(self.UNIFIERS.Object).all())

    @property
    def unique_objects(self) -> List[Predicate]:
        """
        The list of objects. (No specific class is defined)
        """
        return list(
            self.fb.query(self.UNIFIERS.Object)
            .where(self.UNIFIERS.Object.class_name == "object")
            .all()
        )

    @property
    def constraint_violations(self) -> List[Predicate]:
        """
        The list of constraint violations
        """
        return list(self.fb.query(self.UNIFIERS.CV).all())

    @property
    def attribute_values(self) -> List[Predicate]:
        """
        The list of attribute values
        """
        return list(self.fb.query(self.UNIFIERS.AttributeValue).all())

    @property
    def int_attributes(self) -> List[Predicate]:
        """
        The list of attribute values
        """
        return list(self.fb.query(self.UNIFIERS.AttributeInt).all())

    @property
    def user_input(self) -> List[Symbol]:
        """
        The of symbols inside a user predicate
        """
        input_facts = list(
            self.fb.query(self.UNIFIERS.User).select(self.UNIFIERS.User.predicate).all()
        )
        user_fb = unify(
            self.editable_unifiers,
            [f.symbol if type(f) == Raw else f for f in input_facts],
        )

        return user_fb

    def associated_by(self, obj: int, assoc_name: str) -> List[Predicate]:
        """
        The list of associations from object obj via association assoc_name

        Parameters:
            obj (int): The identifier for the object. The method returns association for the object being in either the right or left positions of the given association.
            assoc_name (str): The name of the association to get all objects

        Returns:
            List[Predicate]: List of association from object obj via association assoc_name
        """
        Association = self.UNIFIERS.Association
        q = self.fb.query(Association)
        q1 = q.where(
            ((Association.object_id1 == obj) & (Association.assoc_name == assoc_name))
        )
        q1 = q1.select(Association.object_id2)
        q2 = q.where(
            ((Association.object_id2 == obj) & (Association.assoc_name == assoc_name))
        )
        q2 = q2.select(Association.object_id1)
        return list(q1.all()) + list(q2.all())

    def domains_from(self, start_domain: int) -> int:
        """
        The domain size, it is computed by counting the number of objects in the fact base.
            Parameters:
                start_domain (_type_): The domain where the last grounding was done

            Returns:
                int: The number of objects in the domain larger than start_domain
        """
        q = self.fb.query(self.UNIFIERS.Domain)
        q = q.where(self.UNIFIERS.Domain.object_id > start_domain)
        q = q.select(self.UNIFIERS.Domain.class_name, self.UNIFIERS.Domain.object_id)
        return list(q.all())

    def remove_user(self) -> None:
        """
        Removes all user predicates from the configuration
        """
        users = list(self.fb.query(self.UNIFIERS.User).all())
        for u in users:
            self.fb.remove(u)

    def _remove_facts(self, facts: List[Predicate], remove_user=True) -> None:
        """
        Removes the given facts from the configuration factbase
        """
        for f in facts:
            self.fb.remove(f)
            if remove_user:
                self.fb.remove(self.UNIFIERS.User(Raw(f.symbol)))

    def add_domain(self, class_name: str, object_id: int) -> Predicate:
        """
        Adds a new domain fact `ooasp_domain`
            Parameters:
                class_name: The class name for the ooasp_domain predicate
                object_id: The identifier
            Returns:
                The added fact
        """
        fact = self.UNIFIERS.Domain(class_name=class_name, object_id=object_id)
        self.fb.add(fact)
        return fact

    def add_object(self, object_id: int, class_name: str) -> Predicate:
        """
        Adds a new object predicate to the factbase
            Parameters:
                object_id: The identifier for the object
                class_name: The class name
            Returns:
                The added fact
            Throws:
                Exception if the class of the given name is not a object class
        """
        if not self.kb.is_class(class_name):
            raise RuntimeError(f"{class_name} is not a class")

        fact = self.UNIFIERS.Object(class_name=class_name, object_id=object_id)
        self.fb.add(fact)
        self.consider_as_user([fact])
        return fact

    def add_value(self, object_id: int, attr_name: str, attr_value) -> Predicate:
        """
        Adds a new attribute value predicate to the factbase
            Parameters:
                object_id: The identifier for the object
                attr_name: The name of the attribute
                attr_value: The value of the attribute
            Returns:
                The added fact
        """
        fact = self.UNIFIERS.AttributeValue(
            attr_name=attr_name,
            object_id=object_id,
            attr_value=Raw(parse_term(str(attr_value))),
        )
        self.fb.add(fact)
        self.consider_as_user([fact])
        return fact

    def associate(self, assoc_name: str, object_id1: int, object_id2: int) -> Predicate:
        """
        Adds a new association predicate to the factbase
            Parameters:
                assoc_name: Name of the association
                object_id1: Id of the first object
                object_id1: Id of the second object
            Returns:
                The added fact
        """
        fact = self.UNIFIERS.Association(
            assoc_name=assoc_name, object_id1=object_id1, object_id2=object_id2
        )
        self.fb.add(fact)
        self.consider_as_user([fact])
        return fact

    def remove_object(self, object_id) -> List[Predicate]:
        """
        Removes any object predicates from the factbase associated to the object id
            Parameters:
                object_id: The identifier for the object
            Returns:
                The list of removed facts
        """
        Object = self.UNIFIERS.Object
        q = self.fb.query(Object).where(Object.object_id == object_id)
        objects = list(q.all())
        self._remove_facts(objects)
        return objects

    def remove_value(self, object_id: id, attr_name: str) -> List[Predicate]:
        """
        Removes any existing values for the given attribute of an object in the fact base
            Parameters:
                object_id: The identifier for the object
                attr_name: The name of the attribute
            Returns:
                The list of removed facts
        """
        AttributeValue = self.UNIFIERS.AttributeValue
        q = self.fb.query(AttributeValue)
        q = q.where(
            (
                (AttributeValue.object_id == object_id)
                & (AttributeValue.attr_name == attr_name)
            )
        )
        values = list(q.all())
        self._remove_facts(values)
        return values

    def remove_association(
        self, assoc_name: str, object_id1: int, object_id2: int
    ) -> List[Predicate]:
        """
        Removes the association from the fact base
            Paramters:
                assoc_name: Name of the association
                object_id1: Id of the first object
                object_id1: Id of the second object
            Returns:
                The list of removed facts
        """
        Association = self.UNIFIERS.Association
        q = self.fb.query(Association)
        q = q.where(
            (
                (
                    (
                        (Association.object_id1 == object_id1)
                        & (Association.object_id2 == object_id2)
                    )
                )
                & (Association.assoc_name == assoc_name)
            )
        )
        associations = list(q.all())
        self._remove_facts(associations)
        return associations

    def remove_cvs(self) -> None:
        """
        Removes all the constraint violations
        """
        CV = self.UNIFIERS.CV
        q = self.fb.query(CV)
        cvs = list(q.all())
        self._remove_facts(cvs, remove_user=False)

    def show_cv(self) -> None:
        """
        Prints all the constraint violations on the configuration formated
        """
        cvs = self.constraint_violations
        if len(cvs) == 0:
            print(utils.green("All checks passed!"))
        else:
            for cv in cvs:
                print(utils.red(self.format_cv(cv)))

    def format_cv(self, cv: Predicate):
        """
        Formats a constraint violation Predicate
            Parameters:
                cv: The predicate of class CV
        """
        args = [str(a) for a in cv.args.symbol.arguments]
        return f"Object {cv.object_id}: {cv.info.format(*args)}"

    def all_as_user(self):
        """
        All configuration editable facts as user symbols

        Returns:
            list[Symbol]: User symbols
        """
        return [Function("user", [f.symbol]) for f in self.editable_facts]

    def consider_as_user(self, facts):
        """
        All the given facts are added to the current configuration as user input
        """
        for f in facts:
            self.fb.add(self.UNIFIERS.User(Raw(f.symbol)))

    def save_png(self, directory: str = "./out"):
        """
        Saves the configuration as a png using clingraph
        """
        ctl = Control(["--warn=none"])
        fbs = []
        path = settings.encodings_path.joinpath("viz_config.lp")
        ctl.load(str(path))
        path = settings.encodings_path.joinpath("ooasp_aux_kb.lp")
        ctl.load(str(path))

        ctl.add("base", [], self.fb.asp_str())
        ctl.add("base", [], self.kb.fb.asp_str())
        ctl.ground([("base", [])], ClingraphContext())
        ctl.solve(
            on_model=lambda m: fbs.append(
                Factbase.from_model(m, default_graph="config")
            )
        )
        graphs = compute_graphs(fbs[0])
        render(graphs, format="png", name_format=self.name, directory=directory)

    def view(self):
        """
        Shows the image of the configuration in a jupyter notebook
        """
        self.save_png()
        from IPython.display import Image

        return Image(f"out/{self.name}.png")

    def __str__(self):
        return self.fb.asp_str()
