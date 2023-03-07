% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

#program domain(new_id).


% ooasp_arity(CONFIG, ASSOC, POS, N, ARITY, STEP)
% arity of association ASSOC for object N of class at position POS is ARITY in step STEP

% Arity computed using agregate only for new id
ooasp_arity(ASSOC, 1, new_id, ARITY, new_id) :-
	ooasp_assoc(V,ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),
	ooasp_isa(C1,new_id),
	ARITY = #count { ID2:ooasp_associated(ASSOC,new_id,ID2) },
    use_arity.

ooasp_arity(ASSOC, 2, new_id, ARITY, new_id) :-
	ooasp_assoc(V,ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),
	ooasp_isa(C2,new_id),
	ARITY = #count { ID1:ooasp_associated(ASSOC,ID1,new_id) },
    use_arity.

% Arity of other ids is updated
ooasp_arity(ASSOC, 1, ID1, ARITY+1, new_id) :-
	ooasp_arity(ASSOC, 1, ID1, ARITY, new_id-1),
	ooasp_associated(ASSOC, ID1, new_id),
    use_arity.

ooasp_arity(ASSOC, 2, ID2, ARITY+1, new_id) :-
	ooasp_arity(ASSOC, 2, ID2, ARITY, new_id-1),
	ooasp_associated(ASSOC, new_id, ID2),
    use_arity.

ooasp_arity(ASSOC, 1, ID1, ARITY, new_id) :-
	ooasp_arity(ASSOC, 1, ID1, ARITY, new_id-1),
	not ooasp_associated(ASSOC, ID1, new_id),
    use_arity.

ooasp_arity(ASSOC, 2, ID2, ARITY, new_id) :-
	ooasp_arity( ASSOC, 2, ID2, ARITY, new_id-1),
	not ooasp_associated(ASSOC, new_id, ID2),
    use_arity.


