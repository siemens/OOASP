% Copyright (c) 2024 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

% =====================
% Base program
% =====================


% Target associations are those with cardinality 1..1-MIN..MAX
% We only consider this type of associations for the bound calculations
is_target_assoc(ASSOC,SIDE):-
    ooasp_assoc_limit(ASSOC,max,SIDE,C1,1,C2),
    ooasp_assoc_limit(ASSOC,min,SIDE,C1,1,C2).

is_target_assoc_spec(ASSOC,SIDE):-
    is_target_assoc(ASSOC',SIDE),
    ooasp_assoc_specialization(ASSOC,ASSOC'),
    ooasp_assoc_limit(ASSOC,max,SIDE,C1,1,C2),
    ooasp_assoc_limit(ASSOC,min,SIDE,C1,0,C2).

is_target_assoc_any(ASSOC,SIDE):-is_target_assoc(ASSOC,SIDE).
is_target_assoc_any(ASSOC,SIDE):-is_target_assoc_spec(ASSOC,SIDE).

% =====================
% Incremental generation
% =====================
#program domain(new_object, cls).

% -----------------------------------
% assoc_needs_object(ID1, ASSOC, X, C2, SIDE, new_object)
%   Object ID1 needs at least X objects of class C2 associated by ASSOC
%
%     - Argument new_object is added to the predicate to avoid the redefiniton in following states
%     - We use the idea of "at least" so that when making the intersection (cautious) of models there is
%       no need for optimization.
%
%   The appearance of this predicate in the cautious consequences indicates the need to add
%   at least X objects of type C2 which can be immediately associated to object ID1.

assoc_needs_object(ID1, ASSOC, 1..CMIN - N, C2, SIDE, new_object):-
	lb_violation(lowerbound,ID1,_,(ASSOC,CMIN,N,C2,SIDE,new_object)).

% -----------------------------------
% global_ub_gap(C2,N,new_object).
%   Given a target association ASSOC where each C2 can be associated to at most MAX objects of C1
%   and each C1 has to be associated to exactly one C2.
%   We count the global number of objects of class C2 and this is not enough to cover all C1 objects.
%   Therefore, the upper bound of classes C1 was already reached and we need to add N objects of class C2
%   to fill the gap.
%     - Argument new_object is added to the predicate to avoid the redefiniton in following states
%
%  The appearance of this predicate in the cautious consequences indicates the need to add N objects of type C2

%  EXAMPLE:
%   We can see the use of this predicate in an example with 9 frames and 1 rack.
%   Here, an additional rack is needed since the global upperbound of frames for one rack is 8 but the actual
%   number of frames is 9.
global_ub_gap(C2,1..((NUM1 + MAX - 1) / MAX)-NUM2,new_object):-

    % It is a target association: One side is 1..1 The other side is _..MAX
    is_target_assoc(ASSOC, SIDE),
    ooasp_assoc_limit(ASSOC,max,SIDE2,C2,MAX,C1),
    SIDE2!=SIDE,
    % The number of objects of class C1
    #count { ID:ooasp_isa(C1,ID) } = NUM1,
    % The number of objects of class C2
    #count { ID:ooasp_isa(C2,ID) } = NUM2,
    % The number of objects of class C2 is not sufficient given the number of objects of class C1
    NUM2 * MAX < NUM1,
	active(new_object).

% -----------------------------------
% global_lb_gap(C1,N,new_object).
%   Given a target association ASSOC where each C2 must be associated to at least MIN objects of C1
%   and each C1 has to be associated to exactly one C2.
%   We count the global number of objects of class C1 and this is not enough to cover all C2 lower bounds.
%   Therefore, the lower bound of classes C2 cant be filled and we need to add N objects of class C1.
%   to fill the gap.
%     - Argument new_object is added to the predicate to avoid the redefiniton in following states
%
%  The appearance of this predicate in the cautious consequences indicates the need to add N objects of type C1

%  EXAMPLE:
%   We can see the use of this predicate in an example with 2 frames and 2 racks
%   where additional frames are needed to fill the lower bound of frames needed for the two racks.

global_lb_gap(C1,1..(N2*MIN)-N1,new_object):-
    % It is a target association: One side is 1..1 The other side is MIN.._
    is_target_assoc_any(ASSOC, SIDE),
    SIDE2!=SIDE,
    ooasp_assoc_limit(ASSOC,min,SIDE2,C2,MIN,C1),
    % The number of objects of class C1
    #count { ID:ooasp_isa(C1,ID) } = N1,
    % The number of objects of class C2
    #count { ID:ooasp_isa(C2,ID) } = N2,
    % The number of objects of class C1 is not sufficient given the number of objects of class C2
    N2 * MIN > N1,
	active(new_object).




% -----------------------------------
% association_possible(ASSOC, ID1, ID2, new_object).
%   The association ASSOC bewtwen objects ID1 and ID2 is needed
%   We know that ID1 needs at least one object of class C1 and ID2 needs at least one object of class C2
%   We know that the objects ID1 and ID2 can potentially be associated by ASSOC
%   We also know that the classes of these objects was set by the user or the smart association.
%   This makes sure that the association added does not determine the classes of the objects if not previously given
%
%     - Argument new_object is added to the predicate to avoid the redefiniton in following states
%
%  The appearance of this predicate in the brave consequences indicates that the assocaiation can be added

%  EXAMPLE:
%   We can see the use of this predicate in an example with 17 frames which is slower without it.
association_possible(ASSOC, ID1, ID2, new_object):-
    % We need at least one object of class C2 associated to ID1
	assoc_needs_object(ID1, ASSOC, 1, _, _, new_object),
    % We need at least one object of class C1 associated to ID2
	assoc_needs_object(ID2, ASSOC, 1, _, _, new_object),
    % The objects can be associated
	potential_assoc(ASSOC, ID1, ID2,C1,C2),
    % We would not impose a class by adding an association
	user(ooasp_isa(C1,ID1)),
	user(ooasp_isa(C2,ID2)).
