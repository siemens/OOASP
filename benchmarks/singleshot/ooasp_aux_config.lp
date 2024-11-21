% Copyright (c) 2022-2024 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

% Transitive closure when a leaf class is selected via choice
ooasp_isa(LEAFCLASS,OBJECT) :-
    ooasp_isa_leaf(LEAFCLASS,OBJECT).

% Transitive closure
ooasp_isa(SUPER,OBJECT) :-
    ooasp_isa(SUB,OBJECT),
    ooasp_subclass(SUB,SUPER).

% Generation of leafs
ooasp_isa_leaf(C,OBJECT) :-
    ooasp_isa(C,OBJECT),
	ooasp_leafclass(C).

ooasp_isa_smallest(SUPER,OBJECT) :-
    ooasp_isa(SUPER,OBJECT),
    not ooasp_isa(SUB,OBJECT) :ooasp_subclass(SUB,SUPER).

ooasp_assoc_gen(ASSOC,1,ID1,OBJECT) :-
	ooasp_associated(ASSOC,ID1,OBJECT).

ooasp_assoc_gen(ASSOC,1,OBJECT,ID2) :-
	ooasp_associated(ASSOC,OBJECT,ID2).

ooasp_assoc_gen(ASSOC,2,OBJECT,ID1) :-
	ooasp_associated(ASSOC,ID1,OBJECT).

ooasp_assoc_gen(ASSOC,2,ID2,OBJECT) :-
	ooasp_associated(ASSOC,OBJECT,ID2).

% Association specialization
ooasp_associated(ASSOC,OBJECT,ID2) :-
    ooasp_associated(ASSOC_S,OBJECT,ID2),
    ooasp_assoc_specialization(ASSOC_S,ASSOC),
    ooasp_assoc(ASSOC,C1,_,_,C2,_,_),
    ooasp_isa(C1,OBJECT),
    ooasp_isa(C2,ID2).

ooasp_associated(ASSOC,ID1,OBJECT) :-
    ooasp_associated(ASSOC_S,ID1,OBJECT),
    ooasp_assoc_specialization(ASSOC_S,ASSOC),
    ooasp_assoc(ASSOC,C1,_,_,C2,_,_),
    ooasp_isa(C1,ID1),
    ooasp_isa(C2,OBJECT).

ooasp_associated(ASSOC_S,OBJECT,ID2) :-
    ooasp_associated(ASSOC,OBJECT,ID2),
    ooasp_assoc_specialization(ASSOC_S,ASSOC),
    ooasp_assoc(ASSOC_S,C1,_,_,C2,_,_),
    ooasp_isa(C1,OBJECT),
    ooasp_isa(C2,ID2).

ooasp_associated(ASSOC_S,ID1,OBJECT) :-
    ooasp_associated(ASSOC,ID1,OBJECT),
    ooasp_assoc_specialization(ASSOC_S,ASSOC),
    ooasp_assoc(ASSOC_S,C1,_,_,C2,_,_),
    ooasp_isa(C1,ID1),
    ooasp_isa(C2,OBJECT).


% Int attributes

ooasp_attr_int(OBJECT, A, MIN, MAX):-
	ooasp_isa(C,OBJECT),
	ooasp_attr_minInclusive(C,A,MIN),
	ooasp_attr_maxInclusive(C,A,MAX),
	ooasp_attr(C,A,int).
