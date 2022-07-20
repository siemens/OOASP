% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

% transitive closure
ooasp_subclass(V,SUB,SUPER2):-ooasp_subclass(V,SUB,SUPER1),ooasp_subclass(V,SUPER1,SUPER2).
ooasp_class_and_subclass(V,CLASS,CLASS):- ooasp_class(V,CLASS).
ooasp_class_and_subclass(V,CLASS,SUPER):- ooasp_subclass(V,CLASS,SUPER).

% derive domain for boolean attributes
ooasp_attribute_enum(V,C,N,true):-ooasp_attribute(V,C,N,boolean).
ooasp_attribute_enum(V,C,N,false):-ooasp_attribute(V,C,N,boolean).

% true, if attribute has domain
ooasp_attribute_hasdomain(V,C,N):-ooasp_attribute_enum(V,C,N,D).

ooasp_hassubclass(V,C):-ooasp_subclass(V,SUB,C).
ooasp_hassuperclass(V,C) :- ooasp_subclass(V,C,SUPER).
% leafclasses are classes without subclasses
ooasp_leafclass(V,C):-ooasp_class(V,C),not ooasp_hassubclass(V,C).

% Instantiation
% ooasp_isa(V,C,ID).
% if kb isa instanceof subclass it is also an instanceof superclass
ooasp_isa(CONFIG,SUPER,ID):-ooasp_isa(CONFIG,SUB,ID),ooasp_subclass(V,SUB,SUPER),ooasp_configuration(V,CONFIG).

% configobjects are instantiations of leaf classes
ooasp_configobject(CONFIG,C,ID):-ooasp_leafclass(V,C),ooasp_isa(CONFIG,C,ID),ooasp_configuration(V,CONFIG).

% helper: ooasp_domainandsuperclasses(V,C,ID)
% for an ID and version contains the ooasp_domain-class and it's superclasses
ooasp_domainandsuperclasses(CONFIG,C,ID):-ooasp_domain(CONFIG,C,ID),ooasp_configuration(V,CONFIG).
ooasp_domainandsuperclasses(CONFIG,SUPER,ID):-ooasp_domainandsuperclasses(CONFIG,C,ID),ooasp_subclass(V,C,SUPER),ooasp_configuration(V,CONFIG).

% helper: ooasp_domainandsubclasses(V,C,ID)
ooasp_domainandsubclasses(CONFIG,C,ID):-ooasp_domain(CONFIG,C,ID),ooasp_configuration(V,CONFIG).
ooasp_domainandsubclasses(CONFIG,SUB,ID):-ooasp_domainandsubclasses(CONFIG,C,ID),ooasp_subclass(V,SUB,C),ooasp_configuration(V,CONFIG).

% ooasp_canbe(V,C,ID) Which classes can an ID be
% defines the possible classes an ID could become
ooasp_canbe(CONFIG,C,ID):-ooasp_domainandsubclasses(CONFIG,C,ID).
ooasp_canbe(CONFIG,C,ID):-ooasp_domainandsuperclasses(CONFIG,C,ID).

% ooasp_canbeleafclass(V,C,ID) Which leafclasses can an ID be
ooasp_canbe_leafclass(CONFIG,C,ID):-ooasp_leafclass(V,C),ooasp_canbe(CONFIG,C,ID),ooasp_configuration(V,CONFIG).

