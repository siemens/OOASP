% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

% check instances
ooasp_cv(CONFIG,notinstanceofsubclass(C1,ID1)):-
	ooasp_isa(CONFIG,C1,ID1),
	ooasp_configuration(V,CONFIG),
	ooasp_subclass(V,ANY,C1),
	{ ooasp_isa(CONFIG,C2,ID1):ooasp_subclass(V,C2,C1) } 0.

% count the number of associated objects for every assoc
ooasp_is_associated1(CONFIG,ASSOC,ID1):-ooasp_associated(CONFIG,ASSOC,ID1,ID2).
ooasp_is_associated2(CONFIG,ASSOC,ID2):-ooasp_associated(CONFIG,ASSOC,ID1,ID2).
ooasp_is_associated1_cardinality(CONFIG,ASSOC,ID1,N):- ooasp_is_associated1(CONFIG,ASSOC,ID1), N = #count { ID2:ooasp_associated(CONFIG,ASSOC,ID1,ID2) } .
ooasp_is_associated2_cardinality(CONFIG,ASSOC,ID2,N):- ooasp_is_associated2(CONFIG,ASSOC,ID2), N = #count { ID1:ooasp_associated(CONFIG,ASSOC,ID1,ID2) } .
ooasp_is_associated1_cardinality(CONFIG,ASSOC,ID,0):-ooasp_isa(CONFIG,C1,ID), ooasp_assoc(V,ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),not ooasp_is_associated1(CONFIG,ASSOC,ID).
ooasp_is_associated2_cardinality(CONFIG,ASSOC,ID,0):-ooasp_isa(CONFIG,C2,ID), ooasp_assoc(V,ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),not ooasp_is_associated2(CONFIG,ASSOC,ID).

% check assocs
% there are too few associated objects in the assoc
ooasp_cv(CONFIG,lowerbound1(ASSOC,ID)):-N<C2MIN,ooasp_isa(CONFIG,C1,ID),ooasp_is_associated1_cardinality(CONFIG,ASSOC,ID,N),ooasp_assoc(V,ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),ooasp_configuration(V,CONFIG).
ooasp_cv(CONFIG,lowerbound2(ASSOC,ID)):-N<C1MIN,ooasp_isa(CONFIG,C2,ID),ooasp_is_associated2_cardinality(CONFIG,ASSOC,ID,N),ooasp_assoc(V,ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),ooasp_configuration(V,CONFIG).
ooasp_cv(CONFIG,upperbound1(ASSOC,ID)):-N>C2MAX,ooasp_isa(CONFIG,C1,ID),ooasp_is_associated1_cardinality(CONFIG,ASSOC,ID,N),ooasp_assoc(V,ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),ooasp_configuration(V,CONFIG).
ooasp_cv(CONFIG,upperbound2(ASSOC,ID)):-N>C1MAX,ooasp_isa(CONFIG,C2,ID),ooasp_is_associated2_cardinality(CONFIG,ASSOC,ID,N),ooasp_assoc(V,ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),ooasp_configuration(V,CONFIG).

% type check
ooasp_cv(CONFIG,wrongtypeinassoc1(ASSOC,ID)):-ooasp_is_associated1(CONFIG,ASSOC,ID),ooasp_assoc(V,ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),ooasp_configuration(V,CONFIG), not ooasp_isa(CONFIG,C1,ID).
ooasp_cv(CONFIG,wrongtypeinassoc2(ASSOC,ID)):-ooasp_is_associated2(CONFIG,ASSOC,ID),ooasp_assoc(V,ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),ooasp_configuration(V,CONFIG), not ooasp_isa(CONFIG,C2,ID).

% id is instantiated
ooasp_instantiated(CONFIG,ID):-ooasp_isa(CONFIG,C,ID).

% assoc value must belong to instance
ooasp_cv(CONFIG,no_instance_for_association(CONFIG,ASSOC,ID1)):-ooasp_associated(CONFIG,ASSOC,ID1,ID2),not ooasp_instantiated(CONFIG,ID1).
ooasp_cv(CONFIG,no_instance_for_association(CONFIG,ASSOC,ID2)):-ooasp_associated(CONFIG,ASSOC,ID1,ID2),not ooasp_instantiated(CONFIG,ID2).

% check attributes
ooasp_attribute_hasdomain(V,C,ATTR):-ooasp_attribute_enum(V,C,ATTR,D).

% attribute value must belong to instance
ooasp_cv(CONFIG,no_instance_for_attribute(CONFIG,ATTR,ID)):-ooasp_attribute_value(CONFIG,ATTR,ID,VALUE),not ooasp_instantiated(CONFIG,ID).

ooasp_cv(CONFIG,no_value_from_domain(C,ATTR,ID)):- { ooasp_attribute_value(CONFIG,ATTR,ID,VALUE):ooasp_attribute_enum(V,C,ATTR,VALUE) } 0,ooasp_attribute(V,C,ATTR,T),ooasp_isa(CONFIG,C,ID),ooasp_attribute_hasdomain(V,C,ATTR),ooasp_configuration(V,CONFIG).
ooasp_cv(CONFIG,conflicting_values(C,ATTR,ID)):- ooasp_attribute_value(CONFIG,ATTR,ID,V1),ooasp_attribute_value(CONFIG,ATTR,ID,V2),ooasp_attribute(V,C,ATTR,T),V1!=V2,ooasp_configuration(V,CONFIG).

% TODO: special treatment of inf,sup i.e. Integer.MAX_VALUE,Integer.MIN_VALUE
ooasp_has_value(CONFIG,ATTR,ID):-ooasp_attribute_value(CONFIG,ATTR,ID,VALUE).
ooasp_cv(CONFIG,no_value(ATTR,ID)):- not ooasp_has_value(CONFIG,ATTR,ID),ooasp_attribute(V,C,ATTR,T),ooasp_isa(CONFIG,C,ID),ooasp_configuration(V,CONFIG).
ooasp_cv(CONFIG,value_outside_of_range(ATTR,ID)):- VALUE<MIN,ooasp_attribute_value(CONFIG,ATTR,ID,VALUE),ooasp_attribute(V,C,ATTR,T),ooasp_isa(CONFIG,C,ID),ooasp_attribute_minInclusive(V,C,ATTR,MIN),ooasp_configuration(V,CONFIG).
ooasp_cv(CONFIG,value_outside_of_range(ATTR,ID)):- VALUE>MAX,ooasp_attribute_value(CONFIG,ATTR,ID,VALUE),ooasp_attribute(V,C,ATTR,T),ooasp_isa(CONFIG,C,ID),ooasp_attribute_maxInclusive(V,C,ATTR,MAX),ooasp_configuration(V,CONFIG).

#show ooasp_cv/2.
