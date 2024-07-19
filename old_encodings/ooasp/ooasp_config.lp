% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

% ooasp_configure(CONFIGID)
% this predicate defines, which configuration should be completed 

% instantiation of classes
% An objectid in a ooasp_domain predicate can become an instance of this class
% if it is an instance of the class, it must also become an instance of its leafclasses
0 { ooasp_isa(CONFIG,LEAFCLASS,ID) : ooasp_leafclass(V,LEAFCLASS) , ooasp_canbe(CONFIG,LEAFCLASS,ID) } 1 :- ooasp_domain(CONFIG,C,ID),ooasp_configure(CONFIG),ooasp_configuration(V,CONFIG).

% TODO: symmetry breaking
% this is not very practical for the reconcile task -> there might be "holes" in the ids i.e. ooasp_isa("c1","Wheel",1) ooasp_isa("c1","Wheel",3).
%:- ooasp_domain(CONFIG,C,X),ooasp_domain(CONFIG,C,Y),ooasp_isa(CONFIG,C,Y),X<Y,not ooasp_isa(CONFIG,C,X),ooasp_configure(CONFIG).

% an ID can be only instance of 1 class
%ooasp_cv(CONFIG,isaofunrelatedclasses(I,C1,C2)):-ooasp_isa(CONFIG,C1,I),ooasp_isa(CONFIG,C2,I),C1!=C2,{ ooasp_subclass(V,C1,C2);ooasp_subclass(V,C2,C1) } 0,ooasp_configure(CONFIG).

% Associations
C2MIN { ooasp_associated(CONFIG,ASSOC,ID1,ID2):ooasp_canbe(CONFIG,C2,ID2) }       :- ooasp_isa(CONFIG,C1,ID1),ooasp_assoc(V,ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),ooasp_configuration(V,CONFIG),ooasp_configure(CONFIG), C2MAX = -1.
C2MIN { ooasp_associated(CONFIG,ASSOC,ID1,ID2):ooasp_canbe(CONFIG,C2,ID2) } C2MAX :- ooasp_isa(CONFIG,C1,ID1),ooasp_assoc(V,ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),ooasp_configuration(V,CONFIG),ooasp_configure(CONFIG), C2MAX >= 0.
%C1MIN { ooasp_associated(CONFIG,ASSOC,C1,ID1,C2,ID2):ooasp_canbe(CONFIG,C1,ID1) }       :- ooasp_isa(CONFIG,C2,ID2),ooasp_assoc(V,ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),ooasp_configuration(V,CONFIG),ooasp_configure(CONFIG), C1MAX = -1.
%C1MIN { ooasp_associated(CONFIG,ASSOC,C1,ID1,C2,ID2):ooasp_canbe(CONFIG,C1,ID1) } C1MAX :- ooasp_isa(CONFIG,C2,ID2),ooasp_assoc(V,ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),ooasp_configuration(V,CONFIG),ooasp_configure(CONFIG), C1MAX >= 0.

% type check - only use instantiated object ids
%:- ooasp_associated(CONFIG,ASSOC,C1,ID1,C2,ID2),ooasp_assoc_nobounds(V,ASSOC,C1,C2),not ooasp_isa(CONFIG,C1,ID1),ooasp_configuration(V,CONFIG),ooasp_configure(CONFIG).
%:- ooasp_associated(CONFIG,ASSOC,C1,ID1,C2,ID2),ooasp_assoc_nobounds(V,ASSOC,C1,C2),not ooasp_isa(CONFIG,C2,ID2),ooasp_configuration(V,CONFIG),ooasp_configure(CONFIG).

% Attributes
1 { ooasp_attribute_value(CONFIG,N,ID,VALUE):ooasp_attribute_enum(V,C,N,VALUE) } 1:-ooasp_isa(CONFIG,C,ID),ooasp_attribute(V,C,N,T),ooasp_attribute_hasdomain(V,C,N),ooasp_configuration(V,CONFIG),ooasp_configure(CONFIG).

1 { ooasp_attribute_value(CONFIG,ATTR,ID,VALUE):VALUE=MIN..MAX } 1:-ooasp_attribute(V,C,ATTR,T),
	ooasp_isa(CONFIG,C,ID),
	ooasp_attribute_minInclusive(V,C,ATTR,MIN),
	ooasp_attribute_maxInclusive(V,C,ATTR,MAX),
	ooasp_configuration(V,CONFIG),
	ooasp_configure(CONFIG).

% turn on constraints to complete configuration
:-ooasp_cv(C,I),ooasp_configure(C).

#show ooasp_configobject/3.
#show ooasp_associated/4.
#show ooasp_attribute_value/4.