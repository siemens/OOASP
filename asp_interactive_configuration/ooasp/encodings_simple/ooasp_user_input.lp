% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

#program domain(new_object).

%--------
%  Externals for user selections to allow checks of partial rations
%--------
#external user(ooasp_isa_leaf(LEAFCLASS,new_object)):
	ooasp_leafclass(LEAFCLASS),
	ooasp_domain(C,new_object),
	ooasp_subclass(LEAFCLASS,C).

#external user(ooasp_associated(AS,new_object,ID2)):
	ooasp_domain(C,ID2),
	ooasp_assoc(AS,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX).

#external user(ooasp_associated(AS,ID1,new_object)):
	ooasp_domain(C,ID1),%TODO, is this really needed?
	ooasp_assoc(AS,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX).

#external user(ooasp_attr_value(A,new_object,V)):
	ooasp_attr_enum(C,A,V),%TODO, maybe then remove the C if the A is unique
	ooasp_attr(C,A,T).

ooasp_isa_leaf(LEAFCLASS,new_object) :-
	user(ooasp_isa_leaf(LEAFCLASS,new_object)).
ooasp_associated(AS,new_object,ID2) :-
	user(ooasp_associated(AS,new_object,ID2)).
ooasp_associated(AS,ID1,new_object) :-
	user(ooasp_associated(AS,ID1,new_object)).
ooasp_attr_value(A,new_object,V) :-
	user(ooasp_attr_value(A,new_object,V)).