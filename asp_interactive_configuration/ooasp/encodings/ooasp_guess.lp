% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT


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

1 { ooasp_attr_value(A,new_object,V):V=MIN..MAX } 1:-
	ooasp_attr(C,A,enumint),
	ooasp_isa(C,new_object),
	ooasp_attr_minInclusive(C,A,MIN),
	ooasp_attr_maxInclusive(C,A,MAX),
	guess.

% Numerical Attributes (fclingo)

&fin{MIN..MAX} =: ooasp_attr_fvalue(A,new_object):- 
	% ooasp_isa(C,new_object),
	% ooasp_attr(C,A,int),
	ooasp_attr_int(new_object, A, MIN, MAX),
    guess.
