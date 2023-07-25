% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

#program domain(new_object, cls).

%--------
%  Externals for user selections to allow checks of partial rations
%--------
#external user(ooasp_isa(C,new_object)):
	ooasp_subclass_ref(C,cls).


counts_as(new_object,C2):-ooasp_subclass_ref(cls,C2).
counts_as(new_object,C2):-ooasp_subclass_ref(C2,cls).

#external user(ooasp_associated(AS,new_object,ID2)):
	counts_as(new_object,C1),
	counts_as(ID2,C2),
	ooasp_assoc(AS,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX).

#external user(ooasp_associated(AS,ID1,new_object)):
	counts_as(new_object,C2),
	counts_as(ID1,C1),
	ooasp_assoc(AS,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX).

#external user(ooasp_attr_value(A,new_object,V)):
	ooasp_attr_enum(_,A,V).

ooasp_isa(C,new_object) :-
	user(ooasp_isa(C,new_object)).
ooasp_associated(AS,new_object,ID2) :-
	user(ooasp_associated(AS,new_object,ID2)).
ooasp_associated(AS,ID1,new_object) :-
	user(ooasp_associated(AS,ID1,new_object)).
ooasp_attr_value(A,new_object,V) :-
	user(ooasp_attr_value(A,new_object,V)).