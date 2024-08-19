#program domain(new_object, cls).

% Object ID1 needs one or more objects of class C2 associated by ASSOC
object_needed(ID1, ASSOC, 1..CMIN - N, C2, OPT, new_object):-
	lb_violation(lowerbound,ID1,_,(ASSOC,CMIN,N,C2,OPT,new_object)).


% global_ub(C1,ASSOC,C2,N,new_object).
% Class C1 because of ASSOC needs N C2 more objects based on the maximum.
global_ub(C2,((NUM1 + MAX - 1) / MAX)-NUM2,new_object):-
    % One side is 1..1
    is_target_assoc(ASSOC, OPT),
    % The other side is _..MAX
    OPT2!=OPT,
    ooasp_assoc_limit(ASSOC,max,OPT2,C2,MAX,C1),
    % The numer of elements of class C1
    #count { ID:ooasp_isa(C1,ID) } = NUM1,
    % The numer of elements of class C2
    #count { ID:ooasp_isa(C2,ID) } = NUM2,
    % The amount of elements C2 has already reached the maximum of C1 it can have
    NUM2 * MAX < NUM1,
	active(new_object).

% This works for cases like python ooasp/run.py --frame 2 --rack 2
global_lb(C1,(N2*MIN)-N1,new_object):-
    % One side is 1..1
    is_target_assoc(ASSOC, OPT),
    % The other side is _..MAX
    OPT2!=OPT,
    ooasp_assoc_limit(ASSOC,min,OPT2,C2,MIN,C1),
    % The numer of elements of class C1
    #count { ID:ooasp_isa(C1,ID) } = N1,
    % The numer of elements of class C2
    #count { ID:ooasp_isa(C2,ID) } = N2,
    % The amount of elements C2 has already reached the maximum of C1 it can have
    N2 * MIN > N1,
	active(new_object).

is_target_assoc(ASSOC,OPT):-
    ooasp_assoc_limit(ASSOC,max,OPT,C1,1,C2),
    ooasp_assoc_limit(ASSOC,min,OPT,C1,1,C2).

% An association ASSOC is needed between objects ID1 and ID2
association_needed(ASSOC, ID1, ID2, new_object):-
	object_needed(ID1, ASSOC, 1, _, _, new_object),
	object_needed(ID2, ASSOC, 1, _, _, new_object),
	potential_assoc(ASSOC, ID1, ID2,C1,C2),
	user(ooasp_isa(C1,ID1)),
	user(ooasp_isa(C2,ID2)),
	not user(ooasp_associated(ASSOC, ID1, ID2)).

% association_needed(ID1, new_object, ASSOC):-
% 	object_needed(ID1, ASSOC, 1, _, new_object),
% 	object_needed(new_object, ASSOC, 1, _, new_object),
% 	ooasp_associated(ASSOC, ID1, new_object).

% association_needed(new_object, ID2, ASSOC):-
% 	object_needed(new_object, ASSOC, 1, _, new_object),
% 	object_needed(ID2, ASSOC, 1, _', new_object),
% 	ooasp_associated(ASSOC, new_object, ID2).

#show object_needed/6.
#show global_ub/3.
#show global_lb/3.
#show association_needed/4.
