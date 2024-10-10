% Copyright (c) 2024 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

#program include(new_object, cls).

% Include for performance
ooasp_isa(cls,new_object).

% Fact used in the UI to identify objects that must be included
ooasp_must_be_included(cls,new_object).

% Has to have a leaf class assigned
:- not ooasp_leafclass(LEAFCLASS):
	ooasp_subclass_ref(LEAFCLASS,cls).

#program domain(new_object, cls).

% If an object has a domain, then it could be instanciated
{ ooasp_isa_leaf(LEAFCLASS,new_object):
		ooasp_leafclass(LEAFCLASS),
  		ooasp_subclass_ref(LEAFCLASS,C) } 1:-
  	ooasp_domain(C,new_object),
	guess.

% If is_a appears then it has to be instanciated as leaf
1{ ooasp_isa_leaf(LEAFCLASS,new_object):
		ooasp_leafclass(LEAFCLASS),
  		ooasp_subclass_ref(LEAFCLASS,C) } 1:-
  	ooasp_isa(C,new_object),
	guess.

% % Associations from new_object
{ ooasp_associated(ASSOC,new_object,ID2) } :-
	potential_assoc(ASSOC,new_object,ID2,_,_),
	guess.

potential_assoc(ASSOC,new_object,ID2,C1,C2):-
	ooasp_assoc(ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),
	ooasp_isa(C1,new_object),
	ID2<new_object,
	ooasp_isa(C2,ID2).

{ ooasp_associated(ASSOC,ID1,new_object)} :-
	potential_assoc(ASSOC, ID1, new_object,_,_),
	guess.

potential_assoc(ASSOC, ID1, new_object,C1,C2):-
	ooasp_assoc(ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),
	ooasp_isa(C2,new_object),
	ID1<new_object,
	ooasp_isa(C1,ID1).

% Attributes
1 { ooasp_attr_value(A,new_object,V):
		ooasp_attr_enum(C,A,V) } 1 :-
	ooasp_isa(C,new_object),
	ooasp_attr(C,A,T),
	ooasp_attr_enum(C,A,_),
	guess.

1 { ooasp_attr_value(A,new_object,V):V=MIN..MAX } 1:-
	ooasp_attr(C,A,enumint),
	ooasp_isa(C,new_object),
	ooasp_attr_minInclusive(C,A,MIN),
	ooasp_attr_maxInclusive(C,A,MAX),
	guess.