# Copyright (c) 2022 Siemens AG Oesterreich
# SPDX-License-Identifier: MIT

from typing import List
from types import SimpleNamespace
from clingo import Control
from clorm import Predicate, ConstantField, IntegerField, FactBase, refine_field, parse_fact_files
from clingraph.orm import Factbase
from clingraph.graphviz import compute_graphs, render
from clingraph.clingo_utils import ClingraphContext

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

    def __init__(self, name:str, simplified_encodings=False):
        """
        Creates a knowledge base
            Parameters:
                name: The name of the knowledge base
        """
        self.name:str = name
        self.simplified_encodings = simplified_encodings
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
            if not self.simplified_encodings:
                kb=NameField

        class Class(Predicate):
            class Meta:
                name = "ooasp_class"
            if not self.simplified_encodings:
                kb=NameField
            name=ConstantField

        class SubClass(Predicate):
            class Meta:
                name = "ooasp_subclass"
            if not self.simplified_encodings:
                kb=NameField
            sub_class=ConstantField
            super_class=ConstantField

        class Assoc(Predicate):
            class Meta:
                name = "ooasp_assoc"
            if not self.simplified_encodings:
                kb=NameField
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
                if not self.simplified_encodings:
                    name = "ooasp_attribute"
                else:
                    name = "ooasp_attr"
            if not self.simplified_encodings:
                kb=NameField
            class_name=ConstantField
            name=ConstantField
            type=TypeField

        class AttrMin(Predicate):
            class Meta:
                if not self.simplified_encodings:
                    name = "ooasp_attribute_minInclusive"
                else:
                    name = "ooasp_attr_minInclusive"
            if not self.simplified_encodings:
                kb=NameField
            class_name=ConstantField
            name=ConstantField
            val=IntegerField

        class AttrMax(Predicate):
            class Meta:
                if not self.simplified_encodings:
                    name = "ooasp_attribute_maxInclusive"
                else:
                    name = "ooasp_attr_maxInclusive"
            if not self.simplified_encodings:
                kb=NameField
            class_name=ConstantField
            name=ConstantField
            val=IntegerField

        class AttrEnum(Predicate):
            class Meta:
                if not self.simplified_encodings:
                    name = "ooasp_attribute_enum"
                else:
                    name = "ooasp_attr_enum"
            if not self.simplified_encodings:
                kb=NameField
            class_name=ConstantField
            name=ConstantField
            val=ConstantField

        self.UNIFIERS = SimpleNamespace(
                Class=Class,
                SubClass=SubClass,
                Assoc=Assoc,
                Attr=Attr,
                AttrMin=AttrMin,
                AttrMax=AttrMax,
                AttrEnum=AttrEnum,
                KBName=KBName)

    @property
    def unifiers_list(self):
        """
        The list of all unifiers classes
        """
        return self.UNIFIERS.__dict__.values()

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
    def from_file(cls, name:str, file_path:str, simplified_encodings=False):
        """
        Creates a knowledge base from a file
        """
        kb = cls(name,simplified_encodings)
        kb.load_facts_from_file(file_path)
        return kb

    def direct_subclasses(self, class_name:str)->List:
        """
        Gets all the direct subclasses of a class
            Parameters:
                class_name: The name of the superclass
        """
        SubClass= self.UNIFIERS.SubClass
        return list(self.fb.query(SubClass).where(SubClass.super_class == class_name).select(SubClass.sub_class).all())


    def is_leaf(self, class_name:str)->bool:
        """
        Checks if a class name is a leaf by quering the factbase for any subclasses
            Parameters:
                class_name: The name of the class
        """
        return len(self.direct_subclasses(class_name))==0


    def save_png(self,directory:str="./out")->None:
        """
        Creates the knowledge base as a png using clingraph
        """
        ctl = Control()
        fbs = []
        if self.simplified_encodings:
            ctl.load("./ooasp/encodings_simple/viz_kb.lp")
        else:
            ctl.load("./ooasp/encodings/viz_kb.lp")
        ctl.add("base",[],self.fb.asp_str())
        ctl.ground([("base", [])],ClingraphContext())
        ctl.solve(on_model=lambda m: fbs.append(Factbase.from_model(m,default_graph="kb")))
        graphs = compute_graphs(fbs[0])
        render(graphs,format="png",name_format=self.name,directory=directory)

    def __str__(self):
        return f"%---- OOASPKnowledgeBase ({self.name}) ------\n{self.fb.asp_str()}"