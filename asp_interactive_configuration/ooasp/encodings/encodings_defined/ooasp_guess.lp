% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT


#program domain(new_object, cls).

% Defined domains
{ ooasp_isa_leaf(LEAFCLASS,new_object):
		ooasp_leafclass(LEAFCLASS),
  		ooasp_subclass_ref(LEAFCLASS,C) } 1:-
  	ooasp_domain(C,new_object),
	guess.

1{ ooasp_isa_leaf(LEAFCLASS,new_object):
		ooasp_leafclass(LEAFCLASS),
  		ooasp_subclass_ref(LEAFCLASS,C) } 1:-
  	ooasp_isa(C,new_object),
	guess.

% ooasp_cv(not_instance,new_object,"Yes {} {}",(C,LEAFCLASS)):- ooasp_domain(C,new_object), ooasp_subclass_ref(LEAFCLASS,C), ooasp_leafclass(LEAFCLASS).
% ooasp_cv(not_instance,new_object,"Not an instance",(new_object,)):- ooasp_isa(C,new_object), not ooasp_isa_leaf(_,new_object).
% :- ooasp_isa(C,new_object), not ooasp_isa_leaf(_,new_object). %Not a good idea

% % Associations from new_object
{ ooasp_associated(ASSOC,new_object,ID2) } :-
	ooasp_assoc(ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),
	ooasp_isa(C1,new_object),
	ID2<new_object,
	ooasp_isa(C2,ID2),
	guess.

{ ooasp_associated(ASSOC,ID1,new_object)} :-
	ooasp_assoc(ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),
	ooasp_isa(C2,new_object),
	ID1<new_object,
	ooasp_isa(C1,ID1),
	guess.

% Attributes
1 { ooasp_attr_value(A,new_object,V):
		ooasp_attr_enum(C,A,V) } 1 :-
	ooasp_isa(C,new_object),
	ooasp_attr(C,A,T),
	ooasp_attr_enum(C,A,_),
	guess.

% TODO: this rule is only used if MAX-MIN < 30
1 { ooasp_attr_value(A,new_object,V):V=MIN..MAX } 1:-
	ooasp_attr(C,A,T),
	ooasp_isa(C,new_object),
	ooasp_attr_minInclusive(C,A,MIN),
	ooasp_attr_maxInclusive(C,A,MAX),
	%(MAX-MIN)<30,
	guess.