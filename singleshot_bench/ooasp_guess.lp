% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT


%#program domain(OBJECT, cls).

% If an object has a domain, then it could be instanciated
{ ooasp_isa_leaf(LEAFCLASS,OBJECT):
		ooasp_leafclass(LEAFCLASS),
  		ooasp_subclass_ref(LEAFCLASS,C) } 1:-
  	ooasp_domain(C,OBJECT),
	guess.

% If is_a appears then it has to be instanciated as leaf
1{ ooasp_isa_leaf(LEAFCLASS,OBJECT):
		ooasp_leafclass(LEAFCLASS),
  		ooasp_subclass_ref(LEAFCLASS,C) } 1:-
  	ooasp_isa(C,OBJECT),
	guess.

% % Associations from OBJECT
{ ooasp_associated(ASSOC,OBJECT,ID2) } :-
	ooasp_assoc(ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),
	ooasp_isa(C1,OBJECT),
	ID2<OBJECT,
	ooasp_isa(C2,ID2),
	guess.

{ ooasp_associated(ASSOC,ID1,OBJECT)} :-
	ooasp_assoc(ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),
	ooasp_isa(C2,OBJECT),
	ID1<OBJECT,
	ooasp_isa(C1,ID1),
	guess.

% Attributes
1 { ooasp_attr_value(A,OBJECT,V):
		ooasp_attr_enum(C,A,V) } 1 :-
	ooasp_isa(C,OBJECT),
	ooasp_attr(C,A,T),
	ooasp_attr_enum(C,A,_),
	guess.

1 { ooasp_attr_value(A,OBJECT,V):V=MIN..MAX } 1:-
	ooasp_attr(C,A,enumint),
	ooasp_isa(C,OBJECT),
	ooasp_attr_minInclusive(C,A,MIN),
	ooasp_attr_maxInclusive(C,A,MAX),
	guess.