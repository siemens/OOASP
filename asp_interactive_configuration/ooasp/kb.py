# Copyright (c) 2022 Siemens AG Oesterreich
# SPDX-License-Identifier: MIT

from importlib import resources
from typing import List
from types import SimpleNamespace
from clingo import Control
from clorm import Predicate, ConstantField, IntegerField, FactBase, refine_field, parse_fact_files
from clingraph.orm import Factbase
from clingraph.graphviz import compute_graphs, render
from clingraph.clingo_utils import ClingraphContext
from functools import cache
import ooasp.settings as settings
# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods

class  OOASPKnowledgeBase:
    """
    An OOASP Knowledge Base
    Properties:
            name (str): The name of the kb
            fb (clorm.Factbase): A fact base with the knowledge base
            UNIFIERS (Namespace): All clorm unifiers (classes) used to link objects with predicates
    """

    def __init__(self, name:str):
        """
        Creates a knowledge base
            Parameters:
                name: The name of the knowledge base
        """
        self.name:str = name
        self.set_unifiers()
        self.fb = FactBase()

    def set_unifiers(self):
        """
        Sets the clorm Unifiers based on the name to filter out any other KB defined in the program
        """

        NameField = refine_field(ConstantField,[self.name])

        class KBName(Predicate):
            class Meta:
                name = "ooasp_kb"

        class Class(Predicate):
            class Meta:
                name = "ooasp_class"
            name=ConstantField

        class SubClass(Predicate):
            class Meta:
                name = "ooasp_subclass"
            sub_class=ConstantField
            super_class=ConstantField

        class AssocSpecialization(Predicate):
            class Meta:
                name = "ooasp_assoc_specialization"
            sub_class=ConstantField
            super_class=ConstantField

        class Assoc(Predicate):
            class Meta:
                name = "ooasp_assoc"
            name= ConstantField
            class1=ConstantField
            min1=IntegerField
            max1=IntegerField
            class2=ConstantField
            min2=IntegerField
            max2=IntegerField

        TypeField = refine_field(ConstantField,
        ["int","str","bool"])

        class Attr(Predicate):
            class Meta:
                name = "ooasp_attr"
            class_name=ConstantField
            name=ConstantField
            type=TypeField

        class AttrMin(Predicate):
            class Meta:
                name = "ooasp_attr_minInclusive"
            class_name=ConstantField
            name=ConstantField
            val=IntegerField

        class AttrMax(Predicate):
            class Meta:
                name = "ooasp_attr_maxInclusive"
            class_name=ConstantField
            name=ConstantField
            val=IntegerField

        class AttrEnum(Predicate):
            class Meta:
                name = "ooasp_attr_enum"
            class_name=ConstantField
            name=ConstantField
            val=ConstantField

        class AttrUnique(Predicate):
            class Meta:
                name = "ooasp_unique_attr"
            assoc_name=ConstantField
            class_name=ConstantField
            attr_name=ConstantField

        self.UNIFIERS = SimpleNamespace(
                Class=Class,
                SubClass=SubClass,
                Assoc=Assoc,
                AssocSpecialization=AssocSpecialization,
                Attr=Attr,
                AttrMin=AttrMin,
                AttrMax=AttrMax,
                AttrEnum=AttrEnum,
                AttrUnique=AttrUnique,
                KBName=KBName)

    @property
    def unifiers_list(self):
        """
        The list of all unifiers classes
        """
        return self.UNIFIERS.__dict__.values()


    @property
    # @cache
    def classes(self)->List[Predicate]:
        """
        A list of all classes. Computed via queries to the Factbase
        """
        cls = set(self.fb.query(self.UNIFIERS.Class).select(self.UNIFIERS.Class.name).all())
        cls.remove('object')
        cls = list(cls)
        cls.sort()
        cls=['object'] +cls
        return cls

    @property
    def leafs(self)->List[Predicate]:
        """
        A list of all leafs. Computed via queries to the Factbase
        """
        q = self.fb.query(self.UNIFIERS.Class).select(self.UNIFIERS.Class.name).all()
        leafs = [c for c in q if self.is_leaf(c)]
        return leafs


    def load_facts_from_file(self, file_path:str)->None:
        """
        Adds the facts from a file into the KB factbase
        """
        fb = parse_fact_files([file_path], unifier=self.unifiers_list)
        self.fb.update(fb)

    @classmethod
    def from_file(cls, name:str, file_path:str):
        """
        Creates a knowledge base from a file
        """
        kb = cls(name)
        kb.load_facts_from_file(file_path)
        return kb

    def direct_superclasses(self, class_name:str)->List:
        """
        Gets all the direct superclsses of a class
            Parameters:
                class_name: The name of the subclass
        """
        SubClass= self.UNIFIERS.SubClass
        return list(self.fb.query(SubClass).where(SubClass.sub_class == class_name).select(SubClass.super_class).all())

    def direct_subclasses(self, class_name:str)->List:
        """
        Gets all the direct subclasses of a class
            Parameters:
                class_name: The name of the superclass
        """
        SubClass= self.UNIFIERS.SubClass
        return list(self.fb.query(SubClass).where(SubClass.super_class == class_name).select(SubClass.sub_class).all())


    def associations(self, class_name:str)->List:
        """
        Gets all the associations of a class
            Parameters:
                class_name: The name of the class
        """
        SubClass= self.UNIFIERS.SubClass
        Assoc= self.UNIFIERS.Assoc
        super_classes = self.direct_superclasses(class_name)
        assocs = set()
        for sc in super_classes:
            super_assoc = self.associations(sc)
            assocs.update(super_assoc)
        left = set(self.fb.query(Assoc).where(Assoc.class1 == class_name).select(Assoc.name, Assoc.class2, Assoc.min2, Assoc.max2).all())
        right = set(self.fb.query(Assoc).where(Assoc.class2 == class_name).select(Assoc.name, Assoc.class1, Assoc.min1, Assoc.max1).all())
        assocs.update(left)
        assocs.update(right)
        return assocs


    def is_leaf(self, class_name:str)->bool:
        """
        Checks if a class name is a leaf by quering the factbase for any subclasses
            Parameters:
                class_name: The name of the class
        """
        return len(self.direct_subclasses(class_name))==0

    def is_class(self, class_name:str)->bool:
        """
        Checks if a class name
            Parameters:
                class_name: The name of the class
        """
        return class_name in self.classes

    def save_png(self,directory:str="./out")->None:
        """
        Creates the knowledge base as a png using clingraph
        """
        ctl = Control()
        fbs = []
        path = settings.encodings_path.joinpath("viz_kb.lp")
        ctl.load(str(path))
        ctl.add("base",[],self.fb.asp_str())
        ctl.ground([("base", [])],ClingraphContext())
        ctl.solve(on_model=lambda m: fbs.append(Factbase.from_model(m,default_graph="kb")))
        graphs = compute_graphs(fbs[0])
        render(graphs,format="png",name_format=self.name,directory=directory)

    def __str__(self):
        return f"%---- OOASPKnowledgeBase ({self.name}) ------\n{self.fb.asp_str()}"