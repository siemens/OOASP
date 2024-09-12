% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

#program domain(new_object, cls).

#external active(new_object). % Active id for arity constraints

ooasp_domain(cls,new_object).

ooasp_unused(new_object):- #false: ooasp_isa(C, new_object).

% Transitive closure when a leaf class is selected via choice
ooasp_isa(LEAFCLASS,new_object) :-
    ooasp_isa_leaf(LEAFCLASS,new_object).

% Transitive closure
ooasp_isa(SUPER,new_object) :-
    ooasp_isa(SUB,new_object),
    ooasp_subclass(SUB,SUPER).

% Generation of leafs
ooasp_isa_leaf(C,new_object) :-
    ooasp_isa(C,new_object),
	ooasp_leafclass(C).

ooasp_isa_smallest(SUPER,new_object) :-
    ooasp_isa(SUPER,new_object),
    not ooasp_isa(SUB,new_object) :ooasp_subclass(SUB,SUPER).

% Auxiliary predicate to avoid duplicated rules
% ooasp_assoc_gen(ASSOC,POS,ID1,ID2)
%    Object ID1 apearing in position POS of association ASSOC is associated to object ID2
%    Example: ooasp_assoc_gen(c1,ass,2,23,10): : object 23 of the second class of association ass is associated with object 10

ooasp_assoc_gen(ASSOC,1,ID1,new_object) :-
	ooasp_associated(ASSOC,ID1,new_object).

ooasp_assoc_gen(ASSOC,1,new_object,ID2) :-
	ooasp_associated(ASSOC,new_object,ID2).

ooasp_assoc_gen(ASSOC,2,new_object,ID1) :-
	ooasp_associated(ASSOC,ID1,new_object).

ooasp_assoc_gen(ASSOC,2,ID2,new_object) :-
	ooasp_associated(ASSOC,new_object,ID2).

% Association specialization
ooasp_associated(ASSOC,new_object,ID2) :-
    ooasp_associated(ASSOC_S,new_object,ID2),
    ooasp_assoc_specialization(ASSOC_S,ASSOC),
    ooasp_assoc(ASSOC,C1,_,_,C2,_,_),
    ooasp_isa(C1,new_object),
    ooasp_isa(C2,ID2).

ooasp_associated(ASSOC,ID1,new_object) :-
    ooasp_associated(ASSOC_S,ID1,new_object),
    ooasp_assoc_specialization(ASSOC_S,ASSOC),
    ooasp_assoc(ASSOC,C1,_,_,C2,_,_),
    ooasp_isa(C1,ID1),
    ooasp_isa(C2,new_object).

ooasp_associated(ASSOC_S,new_object,ID2) :-
    ooasp_associated(ASSOC,new_object,ID2),
    ooasp_assoc_specialization(ASSOC_S,ASSOC),
    ooasp_assoc(ASSOC_S,C1,_,_,C2,_,_),
    ooasp_isa(C1,new_object),
    ooasp_isa(C2,ID2).

ooasp_associated(ASSOC_S,ID1,new_object) :-
    ooasp_associated(ASSOC,ID1,new_object),
    ooasp_assoc_specialization(ASSOC_S,ASSOC),
    ooasp_assoc(ASSOC_S,C1,_,_,C2,_,_),
    ooasp_isa(C1,ID1),
    ooasp_isa(C2,new_object).


% Int attributes

ooasp_attr_int(new_object, A, MIN, MAX):-
	ooasp_isa(C,new_object),
	ooasp_attr_minInclusive(C,A,MIN),
	ooasp_attr_maxInclusive(C,A,MAX),
	ooasp_attr(C,A,int).
