% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT


#program domain(new_id).

{ ooasp_isa_leaf(LEAFCLASS,new_id):
		ooasp_leafclass(LEAFCLASS),
  		ooasp_subclass(LEAFCLASS,C) } 1:-
  	ooasp_domain(C,new_id),
	guess.

% % Associations from new_id
{ ooasp_associated(ASSOC,new_id,ID2) } :-
	ooasp_assoc(ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),
	ooasp_isa(C1,new_id),
	ID2<new_id,
	ooasp_isa(C2,ID2),
	guess.

{ ooasp_associated(ASSOC,ID1,new_id)} :-
	ooasp_assoc(ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),
	ooasp_isa(C2,new_id),
	ID1<new_id,
	ooasp_isa(C1,ID1),
	guess.

% Attributes
1 { ooasp_attr_value(A,new_id,V):
		ooasp_attr_enum(C,A,V) } 1 :-
	ooasp_isa(C,new_id),
	ooasp_attr(C,A,T),
	ooasp_attr_hasdomain(C,A),
	guess.

% TODO: this rule is only used if MAX-MIN < 30
1 { ooasp_attr_value(A,new_id,V):V=MIN..MAX } 1:-
	ooasp_attr(C,A,T),
	ooasp_isa(C,new_id),
	ooasp_attr_minInclusive(C,A,MIN),
	ooasp_attr_maxInclusive(C,A,MAX),
	%(MAX-MIN)<30,
	guess.