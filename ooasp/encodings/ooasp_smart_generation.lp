% =====================
% Base program
% =====================


% Target associations are those with cardinality 1..1-MIN..MAX
% We only consider this type of associations for the bound calculations
is_target_assoc(ASSOC,SIDE):-
    ooasp_assoc_limit(ASSOC,max,SIDE,C1,1,C2),
    ooasp_assoc_limit(ASSOC,min,SIDE,C1,1,C2).

% =====================
% Incremental generation
% =====================
#program domain(new_object, cls).

% #heuristic object_needed(ID1, ASSOC, A, C2, SIDE, new_object):object_needed(ID1, ASSOC, A, C2, SIDE, new_object),ooasp_assoc_specialization(ASSOC,_). [1,sign]
% -----------------------------------
% object_needed(ID1, ASSOC, X, C2, SIDE, new_object)
%   Object ID1 needs at least X objects of class C2 associated by ASSOC
%
%     - Argument new_object is added to the predicate to avoid the redefiniton in following states
%     - We use the idea of "at least" so that when making the intersection (cautious) of models there is
%       no need for optimization.
%
%   The appearance of this predicate in the cautious consequences indicates the need to add
%   at least X objects of type C2 which can be immediately associated to object ID1.

object_needed(ID1, ASSOC, 1..CMIN - N, C2, SIDE, new_object):-
	lb_violation(lowerbound,ID1,_,(ASSOC,CMIN,N,C2,SIDE,new_object)).

% -----------------------------------
% global_ub(C2,N,new_object).
%   Given a target association ASSOC where each C2 can be associated to at most MAX objects of C1
%   and each C1 has to be associated to exactly one C2.
%   We count the global number of objects of class C2 and this is not enough to cover all C2 objects
%   therefore the upper bound of classes C2 was already reached and we need to add N objects of class C2
%   to fill the gap.
%     - Argument new_object is added to the predicate to avoid the redefiniton in following states
%
%  The appearance of this predicate in the cautious consequences indicates the need to add N objects of type C2

%  EXAMPLE:
%   We can see the use of this predicate in an example with 9 frames and 1 rack.
%   Where the need for one more rack since the upperbound of rack is 8 and the number of frames is 9.
global_ub(C2,((NUM1 + MAX - 1) / MAX)-NUM2,new_object):-
    % It is a target association: One side is 1..1 The other side is _..MAX
    is_target_assoc(ASSOC, SIDE),
    ooasp_assoc_limit(ASSOC,max,SIDE2,C2,MAX,C1),
    SIDE2!=SIDE,
    % The numer of elements of class C1
    #count { ID:ooasp_isa(C1,ID) } = NUM1,
    % The numer of elements of class C2
    #count { ID:ooasp_isa(C2,ID) } = NUM2,
    % The amount of elements C2 has already reached the maximum of C1 it can have
    NUM2 * MAX < NUM1,
	active(new_object).

% -----------------------------------
% global_lb(C1,N,new_object).
%   Given a target association ASSOC where each C2 can be associated to at least MIN objects of C1
%   and each C1 has to be associated to exactly one C2.
%   We count the global number of objects of class C1 and this is not enough to cover all C2 lower bounds.
%   Therefore the lower bound of classes C2 cant be filled and we need to add N objects of class C1.
%   to fill the gap.
%     - Argument new_object is added to the predicate to avoid the redefiniton in following states
%
%  The appearance of this predicate in the cautious consequences indicates the need to add N objects of type C1

%  EXAMPLE:
%   We can see the use of this predicate in an example with 2 frames 2 racks.
%   Where the need the additional frames to fill the lower bound of racks.

global_lb(C1,(N2*MIN)-N1,new_object):-
    % It is a target association: One side is 1..1 The other side is MIN.._
    is_target_assoc(ASSOC, SIDE),
    SIDE2!=SIDE,
    ooasp_assoc_limit(ASSOC,min,SIDE2,C2,MIN,C1),
    % The numer of elements of class C1
    #count { ID:ooasp_isa(C1,ID) } = N1,
    % The numer of elements of class C2
    #count { ID:ooasp_isa(C2,ID) } = N2,
    % The amount of elements C1 does not fill the lowe bound of C2
    N2 * MIN > N1,
	active(new_object).

% -----------------------------------
% association_needed(ASSOC, ID1, ID2, new_object).
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
association_needed(ASSOC, ID1, ID2, new_object):-
    % We need at least one object of class C2 associated to ID1
	object_needed(ID1, ASSOC, 1, _, _, new_object),
    % We need at least one object of class C1 associated to ID2
	object_needed(ID2, ASSOC, 1, _, _, new_object),
    % The objects can be associated
	potential_assoc(ASSOC, ID1, ID2,C1,C2),
    % We would not impose a class by adding an association
	user(ooasp_isa(C1,ID1)),
	user(ooasp_isa(C2,ID2)).