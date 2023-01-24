# Copyright (c) 2022 Siemens AG Oesterreich
# SPDX-License-Identifier: MIT

from typing import List
from types import SimpleNamespace
from clingo import Model, parse_term
from clorm.clingo import Control
from clorm import Symbol, Predicate, ConstantField, IntegerField, FactBase, RawField, refine_field, Raw, StringField
from clingraph.orm import Factbase
from clingraph.graphviz import compute_graphs, render
from .kb import OOASPKnowledgeBase
from copy import deepcopy
import ooasp.utils as utils


class  OOASPConfiguration:
    """
    An OOASP Configuration
    Properties:
            kb (OOASPKnowledgeBase): The Knowledge base
            name (str): The name of the configuration
            fb (clorm.Factbase): A fact base with the configuration
            UNIFIERS (Namespace): All clorm unifiers (classes) used to link objects with predicates
    """

    def __init__(self, name:str, kb: OOASPKnowledgeBase):
        """
        Creates a possibly partial configuration
            Parameters:
                config: The name of the configuration
                kb: The Knowledge base
        """
        self.name:str = name
        self.kb:str = kb
        self.set_unifiers()
        self.fb = FactBase()

    def __deepcopy__(self, memo):
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
        
        NameField = refine_field(ConstantField,[self.name])
        class ConfigObject(Predicate):
            class Meta:
                name = "ooasp_configobject"

            config=NameField(default=self.name)
            class_name=ConstantField
            object_id=IntegerField

        class Leaf(Predicate):
            class Meta:
             name = "ooasp_isa_leaf"
            config=NameField(default=self.name)
            class_name=ConstantField
            object_id=IntegerField

        class AttributeValue(Predicate):
            class Meta:
                name = "ooasp_attribute_value"

            config=NameField(default=self.name)
            attr_name=ConstantField
            object_id=IntegerField
            attr_value=RawField

        class Association(Predicate):
            class Meta:
                name = "ooasp_associated"

            config=NameField(default=self.name)
            assoc_name=ConstantField
            object_id1=IntegerField
            object_id2=IntegerField

        class Domain(Predicate):
            class Meta:
                name = "ooasp_domain"

            config=NameField(default=self.name)
            class_name=ConstantField
            object_id=IntegerField

        
        class CV(Predicate):
            class Meta:
                name = "ooasp_cv"

            config=NameField(default=self.name)
            name=ConstantField
            object_id=IntegerField
            info=StringField
            args=RawField

        class User(Predicate):
            class Meta:
                name = "user"

            predicate=RawField

        
        self.UNIFIERS = SimpleNamespace(
                AttributeValue=AttributeValue,
                Association=Association,
                Leaf=Leaf,
                ConfigObject=ConfigObject,
                Domain=Domain,
                CV=CV,
                User=User)

    @classmethod
    def from_model(cls, name:str, kb: OOASPKnowledgeBase, model:Model):
        """
        Creates a configuration from a clingo model
            Parameters:
                name: The name of the configuration
                kb: The knowledge base
                model: The clingo model
        """
        config= cls(name=name, kb = kb)
        config.fb = model.facts(unifier=config.unifiers_list,atoms=True,shown=True)
        return config

    @property
    def unifiers_list(self)->List:
        """
        The list of all unifiers classes
        """
        return self.UNIFIERS.__dict__.values()
    
    @property
    def domain_size(self)->int:
        """
        The domain size, it is computed by counting the number of objects in the fact base.
        """
        return self.fb.query(self.UNIFIERS.Domain).select(self.UNIFIERS.Domain.object_id).count()

    @property
    def has_cv(self)->bool:
        """
        True if the configuration has any constraint violations, false otherwise
        """
        return len(self.constraint_violations) != 0

    @property
    def editable_unifiers(self)->List:
        """
        List of all unifier classes that are editable: Leaf,AttributeValue,Association
        """
        return [self.UNIFIERS.Leaf,self.UNIFIERS.AttributeValue,self.UNIFIERS.Association]

    @property
    def editable_facts(self)->List[Predicate]:
        """
        The list of all facts in the fact base that are editable.
        Editable facts are leaf class, attribute value and associations.
        """
        return self.associations + self.leafs + self.attribute_values

    @property
    def assumptions(self)->List[Symbol]:
        """
        The symbols for all editable facts in the configuration
        """
        return [f.symbol for f in self.editable_facts]

    @property
    def associations(self)->List[Predicate]:
        """
        The list of associations
        """
        return list(self.fb.query(self.UNIFIERS.Association).all())

    @property
    def leafs(self)->List[Predicate]:
        """
        The list of leafs
        """
        return list(self.fb.query(self.UNIFIERS.Leaf).all())

    @property
    def constraint_violations(self)->List[Predicate]:
        """
        The list of constraint violations
        """
        return list(self.fb.query(self.UNIFIERS.CV).all())

    @property
    def attribute_values(self)->List[Predicate]:
        """
        The list of attribute values
        """
        return list(self.fb.query(self.UNIFIERS.AttributeValue).all())

    @property
    def user_input(self)->List[Symbol]:
        """
        The of symbols inside a user predicate
        """
        input_facts = list(self.fb.query(self.UNIFIERS.User).select(self.UNIFIERS.User.predicate).all())
        return [f.symbol for f in input_facts]

    def remove_user(self)->None:
        """
        Removes all user predicates from the configuration
        """
        users = list(self.fb.query(self.UNIFIERS.User).all())
        for u in users:
            self.fb.remove(u)

    def _remove_facts(self,facts:List[Predicate])->None:
        """
        Removes the given facts from the configuration factbase
        """
        for f in facts:
            self.fb.remove(f)

    def add_domain(self, class_name:str, object_id:int)->Predicate:
        """
        Adds a new domain fact `ooasp_domain`
            Parameters:
                class_name: The class name for the ooasp_domain predicate
                object_id: The identifier
            Returns:
                The added fact
        """
        fact = self.UNIFIERS.Domain(class_name=class_name,object_id=object_id)
        self.fb.add(fact)
        return fact
    
    def add_leaf(self,object_id:int, class_name:str)->Predicate:
        """
        Adds a new leaf predicate to the factbase
            Parameters:
                object_id: The identifier for the object
                class_name: The class name
            Returns:
                The added fact
            Throws:
                Exception if the class of the given name is not a leaf class
        """
        if not self.kb.is_leaf(class_name):
            raise RuntimeError(f"{class_name} is not a leaf class")

        fact = self.UNIFIERS.Leaf(class_name=class_name,object_id=object_id)
        self.fb.add(fact)
        return fact

    def add_value(self, object_id:int, attr_name:str, attr_value)->Predicate:
        """
        Adds a new attribute value predicate to the factbase
            Parameters:
                object_id: The identifier for the object
                attr_name: The name of the attribute
                attr_value: The value of the attribute
            Returns:
                The added fact
        """
        fact = self.UNIFIERS.AttributeValue(attr_name=attr_name,
            object_id=object_id,
            attr_value=Raw(parse_term(str(attr_value))))
        self.fb.add(fact)
        return fact

    def add_association(self, assoc_name:str,object_id1:int,object_id2:int)->Predicate:
        """
        Adds a new association predicate to the factbase
            Parameters:
                assoc_name: Name of the association
                object_id1: Id of the first object
                object_id1: Id of the second object
            Returns:
                The added fact
        """
        fact = self.UNIFIERS.Association(assoc_name=assoc_name,
            object_id1=object_id1,
            object_id2=object_id2)
        self.fb.add(fact)
        return fact

    def remove_leaf(self, object_id)->List[Predicate]:
        """
        Removes any leaf predicates from the factbase associated to the object id
            Parameters:
                object_id: The identifier for the object
            Returns:
                The list of removed facts
        """
        Leaf = self.UNIFIERS.Leaf
        q = self.fb.query(Leaf).where(Leaf.object_id == object_id)
        leafs = list(q.all())
        self._remove_facts(leafs)
        return leafs

    def remove_value(self, object_id:id, attr_name:str)->List[Predicate]:
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
        q = q.where(((AttributeValue.object_id == object_id) & (AttributeValue.attr_name == attr_name)))
        values = list(q.all())
        self._remove_facts(values)
        return values

    def remove_association(self, assoc_name:str, object_id1:int, object_id2:int)->List[Predicate]:
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
        q = q.where(((((Association.object_id1 == object_id1) &\
                        (Association.object_id2 == object_id2))) &\
                        (Association.assoc_name == assoc_name)))
        associations = list(q.all())
        self._remove_facts(associations)
        return associations


    def show_cv(self)->None:
        """
        Prints all the constraint violations on the configuration formated
        """
        cvs = self.constraint_violations
        if len(cvs)==0:
            print(utils.green('All checks passed!'))
        else:
            for cv in cvs:
                print(utils.red(self.format_cv(cv)))

    def format_cv(self,cv:Predicate):
        """
        Formats a constraint violation Predicate
            Parameters:
                cv: The predicate of class CV
        """
        args = [str(a) for a in cv.args.symbol.arguments]
        return f"Object {cv.object_id}: {cv.info.format(*args)}"

    def save_png(self,directory:str="./out"):
        """
        Saves the configuration as a png using clingraph
        """
        ctl = Control(['--warn=none'])
        fbs = []
        ctl.load("./ooasp/encodings/viz_config.lp")
        ctl.load("./ooasp/encodings/ooasp_aux_kb.lp")
        ctl.add("base",[],self.fb.asp_str())
        ctl.add("base",[],self.kb.fb.asp_str())
        ctl.ground([("base", [])])
        ctl.solve(on_model=lambda m: fbs.append(Factbase.from_model(m,default_graph="config")))
        graphs = compute_graphs(fbs[0])
        render(graphs,format="png",name_format=self.name,directory=directory)

    def view(self):
        """
        Shows the image of the configuration in a jupyter notebook
        """
        self.save_png()
        from IPython.display import Image
        return Image(f"out/{self.name}.png")

    def __str__(self):
        return self.fb.asp_str()

