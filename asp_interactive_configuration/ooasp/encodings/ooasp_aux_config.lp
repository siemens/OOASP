% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

#program domain(new_id).

#external active(new_id). % Active id for arity constraints


ooasp_domain(CONFIG,object,new_id):-ooasp_configuration(_,CONFIG).

% Transitive closure for the new id
ooasp_isa(CONFIG,LEAFCLASS,new_id) :-
    ooasp_isa_leaf(CONFIG,LEAFCLASS,new_id).

ooasp_isa(CONFIG,SUPER,new_id) :-
    ooasp_configuration(V,CONFIG),
    ooasp_isa(CONFIG,SUB,new_id),
    ooasp_subclass(V,SUB,SUPER).

% Auxiliary predicate to avoid duplicated rules
% ooasp_associated_general(CONFIG,ASSOC,POS,ID1,ID2)
%    Object ID1 apearing in position POS of association ASSOC is associated to object ID2
%    Example: ooasp_associated_general(c1,ass,2,23,10): : object 23 of the second class of association ass is associated with object 10

ooasp_associated_general(CONFIG,ASSOC,1,ID1,new_id) :-
	ooasp_associated(CONFIG,ASSOC,ID1,new_id).

ooasp_associated_general(CONFIG,ASSOC,1,new_id,ID2) :-
	ooasp_associated(CONFIG,ASSOC,new_id,ID2).

ooasp_associated_general(CONFIG,ASSOC,2,new_id,ID1) :-
	ooasp_associated(CONFIG,ASSOC,ID1,new_id).

ooasp_associated_general(CONFIG,ASSOC,2,ID2,new_id) :-
	ooasp_associated(CONFIG,ASSOC,new_id,ID2).


