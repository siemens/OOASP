#program domain(new_object, cls).

% upper_filled(C1,ASSOC,C2,N,new_object).
% Class C1 because of ASSOC needs N C2 more objects based on the maximum.
upper_filled(C1,ASSOC,C2,((NUM1 + MAX - 1) / MAX)-NUM2,new_object):-
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
lower_global(C1,ASSOC,C2,(NUM2*MIN)-NUM1,new_object):-
    % One side is 1..1
    is_target_assoc(ASSOC, OPT),
    % The other side is _..MAX
    OPT2!=OPT,
    ooasp_assoc_limit(ASSOC,min,OPT2,C2,MIN,C1),
    % The numer of elements of class C1
    #count { ID:ooasp_isa(C1,ID) } = NUM1,
    % The numer of elements of class C2
    #count { ID:ooasp_isa(C2,ID) } = NUM2,
    % The amount of elements C2 has already reached the maximum of C1 it can have
    NUM2 * MIN > NUM1,
	active(new_object).

is_target_assoc(ASSOC,OPT):-
    ooasp_assoc_limit(ASSOC,max,OPT,C1,1,C2),
    ooasp_assoc_limit(ASSOC,min,OPT,C1,1,C2).