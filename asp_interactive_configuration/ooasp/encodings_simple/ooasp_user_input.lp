% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

#program domain(new_id).

%--------
%  Externals for user selections to allow checks of partial rations
%--------
#external user(ooasp_isa_leaf(LEAFCLASS,new_id)):
	ooasp_leafclass(LEAFCLASS),
	ooasp_domain(C,new_id),
	ooasp_subclass(LEAFCLASS,C).

#external user(ooasp_associated(AS,new_id,ID2)):
	ooasp_domain(C,ID2),
	ooasp_assoc(AS,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX).

#external user(ooasp_associated(AS,ID1,new_id)):
	ooasp_domain(C,ID1),
	ooasp_assoc(AS,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX).

#external user(ooasp_attr_value(A,new_id,V)):
	ooasp_attr_enum(C,A,V),
	ooasp_attr(C,A,T).

ooasp_isa_leaf(LEAFCLASS,new_id) :-
	user(ooasp_isa_leaf(LEAFCLASS,new_id)).
ooasp_associated(AS,new_id,ID2) :-
	user(ooasp_associated(AS,new_id,ID2)).
ooasp_associated(AS,ID1,new_id) :-
	user(ooasp_associated(AS,ID1,new_id)).
ooasp_attr_value(A,new_id,V) :-
	user(ooasp_attr_value(A,new_id,V)).