% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

% type check and cardinalities
%  TODO: find general solution
% assoc1_constraint(ASSOC,C1,CARD,C2)
% currently this means: In the ASSOC all elements of C1 are associated with exactly CARD of C2 and nothing else
assoc1_constraint(element_modules,elementA,1,moduleI).
assoc1_constraint(element_modules,elementB,2,moduleII).
assoc1_constraint(element_modules,elementC,3,moduleIII).
assoc1_constraint(element_modules,elementD,4,moduleIV).

ooasp_potential_cv(customlowerbound).
ooasp_potential_cv(racksinglelowerbound).
ooasp_potential_cv(rackdoublelowerbound).
ooasp_potential_cv(module_requires_element).
ooasp_potential_cv(moduleII_requires_moduleV).

#program domain(new_object).


ooasp_cv(assoc1_constraint1,new_object,"Asssociated by {} to {} which is not of type {}",(new_object,ASSOC,ID2,C2)) :-
    ooasp_assoc(C,ASSOC,new_object,ID2),
    assoc1_constraint(ASSOC,C1,CARD,C2),
    ooasp_isa(C1,new_object),
    not ooasp_isa(C2,ID2).

ooasp_cv(assoc1_constraint1,new_object,"Asssociated by {} to {} which is not of type {}",(new_object,ASSOC,ID2,C2)) :-
    ooasp_assoc(C,ASSOC,new_object,ID2),
    assoc1_constraint(ASSOC,C1,CARD,C2),
    not ooasp_isa(C1,new_object),
    ooasp_isa(C2,ID2).

ooasp_cv(assoc1_constraint2,new_object,"Asssociated by {} to {} which is not of type {}",(new_object,ASSOC,ID1,C1)) :-
    ooasp_assoc(C,ASSOC,ID1,new_object),
    assoc1_constraint(ASSOC,C1,CARD,C2),
    not ooasp_isa(C1,ID1),
    ooasp_isa(C2,new_object).

ooasp_cv(assoc1_constraint2,new_object,"Asssociated by {} to {} which is not of type {}",(new_object,ASSOC,ID1,C1)) :-
    ooasp_assoc(C,ASSOC,ID1,new_object),
    assoc1_constraint(ASSOC,C1,CARD,C2),
    ooasp_isa(C1,ID1),
    not ooasp_isa(C2,new_object).

ooasp_cv(customlowerbound,ID,"Custom lowerbound for association {} not reached: {}",(ASSOC,CARD,new_object)):-
    #count { ID2:ooasp_assoc_gen(ASSOC,1,ID,ID2) } < CARD,
    ooasp_isa(C1,ID),
    assoc1_constraint(ASSOC,C1,CARD,C2),
	active(new_object).

ooasp_cv(customupperbound,ID,"Custom upperbound for association {} not reached: {}",(ASSOC,CARD,new_object)):-
    #count { ID2:ooasp_assoc_gen(ASSOC,1,ID,ID2) } > CARD,
    assoc1_constraint(ASSOC,C1,CARD,C2),
    ooasp_isa(C1,ID),
	active(new_object).


% rack_frames
ooasp_cv(racksinglelowerbound,ID,"Rack singles should be associated to 4 frames ",(new_object,)) :-
    ooasp_isa(rackSingle,ID),
    #count { ID2:ooasp_assoc_gen(ASSOC,1,ID,ID2) } < 4,
	active(new_object).

ooasp_cv(racksingleupperbound,ID,"Rack singles should be associated to 4 frames ",(new_object,)) :-
    ooasp_isa(rackSingle,ID),
    #count { ID2:ooasp_assoc_gen(ASSOC,1,ID,ID2) } > 4,
	active(new_object).


ooasp_cv(rackdoublelowerbound,ID,"Rack doubles should be associated to 8 frames ",(new_object,)) :-
    ooasp_isa(rackDouble,ID),
    #count { ID2:ooasp_assoc_gen(ASSOC,1,ID,ID2) } < 8,
	active(new_object).

ooasp_cv(rackdoubleupperbound,ID,"Rack doubles should be associated to 8 frames ",(new_object,)) :-
    ooasp_isa(rackDouble,ID),
    #count { ID2:ooasp_assoc_gen(ASSOC,1,ID,ID2) } > 8,
	active(new_object).


ooasp_cv(module_requires_element,ID,"Modules of type {} must have at least one element",(LEAFCLASS,new_object)) :-
    #count { ID2:ooasp_assoc_gen(element_modules,2,ID,ID2) } == 0,
	active(new_object),
    ooasp_isa(module,ID),
    ooasp_isa_leaf(C,LEAFCLASS,ID),
    LEAFCLASS != moduleV.


ooasp_cv(module_requires_element,ID,"Modules of type {} must have at least one element",(LEAFCLASS,new_object)) :-
	ooasp_arity(C,element_modules, 2, ID, ARITY, new_object),
	active(new_object),
    ooasp_isa(module,ID),
    ooasp_isa_leaf(C,LEAFCLASS,ID),
    LEAFCLASS != moduleV,
    ARITY==0.

ooasp_cv(frame_position_must_be_unique, new_object, "Frame position is equal to the one of frame {} ",(F,)):-
    ooasp_assoc(C,rack_frames,R,new_object),
    ooasp_assoc(C,rack_frames,R,F),
    new_object!=F,
    ooasp_attr_value(C,frame_position,new_object,P),
    ooasp_attr_value(C,frame_position,F,P).

ooasp_cv(frame_position_must_be_unique, F1, "Frame position is equal to the one of frame {} ",(F2,new_object)):-
    ooasp_assoc(C,rack_frames,new_object,F1),
    ooasp_assoc(C,rack_frames,new_object,F2),
    F1!=F2,
    ooasp_attr_value(C,frame_position,F1,P),
    ooasp_attr_value(C,frame_position,F2,P).

% frame positions for racksingle
ooasp_cv(frame_must_be_within_range, new_object, "Frame position is outside of range {} ",(new_object,)):-
    ooasp_isa(rackSingle,ID),
    ooasp_assoc(C,rack_frames,ID,new_object),
    ooasp_attr_value(C,frame_position,F,P),
    P<1.

ooasp_cv(frame_must_be_within_range, new_object, "Frame position is outside of range {} ",(new_object,)):-
    ooasp_isa(rackSingle,ID),
    ooasp_assoc(C,rack_frames,ID,new_object),
    ooasp_attr_value(C,frame_position,F,P),
    P>4.

ooasp_cv(frame_must_be_within_range, F, "Frame position is outside of range {} ",(F,new_object)):-
    ooasp_isa(rackSingle,new_object),
    ooasp_assoc(C,rack_frames,new_object,F),
    ooasp_attr_value(C,frame_position,F,P),
    P<1.

ooasp_cv(frame_must_be_within_range, F, "Frame position is outside of range {} ",(F,new_object)):-
    ooasp_isa(rackSingle,new_object),
    ooasp_assoc(C,rack_frames,new_object,F),
    ooasp_attr_value(C,frame_position,F,P),
    P>4.

% frame positions for rackdouble
ooasp_cv(frame_must_be_within_range, new_object, "Frame position is outside of range {} ",(new_object,)):-
    ooasp_isa(rackDouble,ID),
    ooasp_assoc(C,rack_frames,ID,new_object),
    ooasp_attr_value(C,frame_position,F,P),
    P<1.

ooasp_cv(frame_must_be_within_range, new_object, "Frame position is outside of range {} ",(new_object,)):-
    ooasp_isa(rackDouble,ID),
    ooasp_assoc(C,rack_frames,ID,new_object),
    ooasp_attr_value(C,frame_position,F,P),
    P>8.

ooasp_cv(frame_must_be_within_range, F, "Frame position is outside of range {} ",(F,new_object)):-
    ooasp_isa(rackDouble,new_object),
    ooasp_assoc(C,rack_frames,new_object,F),
    ooasp_attr_value(C,frame_position,F,P),
    P<1.

ooasp_cv(frame_must_be_within_range, F, "Frame position is outside of range {} ",(F,new_object)):-
    ooasp_isa(rackDouble,new_object),
    ooasp_assoc(C,rack_frames,new_object,F),
    ooasp_attr_value(C,frame_position,F,P),
    P>8.

% moduleII requires moduleV
% TODO: Is using active(new_object) enough?
ooasp_cv(moduleII_requires_moduleV,F,"ModuleII requires moduleV in frame {} new_object {} {} {}",(F,new_object,NROFMODULEII,NROFMODULEV)):-
    active(new_object),
    ooasp_isa(frame,F),
    NROFMODULEII = #count { M:ooasp_assoc(C,frame_modules,F,M),ooasp_isa(moduleII,M) },
    NROFMODULEV = #count { M:ooasp_assoc(C,frame_modules,F,M),ooasp_isa(moduleV,M) },
    NROFMODULEII > 0,
    NROFMODULEV = 0.

ooasp_cv(moduleII_requires_moduleV,F,"ModuleII requires moduleV in frame {} new_object {} {} {}",(F,new_object,NROFMODULEII,NROFMODULEV)):-
    active(new_object),
    ooasp_isa(frame,F),
    NROFMODULEII = #count { M:ooasp_assoc(C,frame_modules,F,M),ooasp_isa(moduleII,M) },
    NROFMODULEV = #count { M:ooasp_assoc(C,frame_modules,F,M),ooasp_isa(moduleV,M) },
    NROFMODULEII = 0,
    NROFMODULEV > 0.

% new frame
%ooasp_cv(moduleII_requires_moduleV,new_object,"ModuleII requires moduleV in frame1 {} new_object {} {} {}",(new_object,new_object,NROFMODULEII,NROFMODULEV)):-
%    active(new_object),
%    ooasp_isa(frame,new_object),
%    NROFMODULEII = #count { M:ooasp_assoc(C,frame_modules,new_object,M),ooasp_isa(moduleII,M) },
%    NROFMODULEV = #count { M:ooasp_assoc(C,frame_modules,new_object,M),ooasp_isa(moduleV,M) },
%    NROFMODULEII > 0,
%    NROFMODULEV = 0.

%ooasp_cv(moduleII_requires_moduleV,new_object,"ModuleII requires moduleV in frame2 {} new_object {} {} {}",(new_object,new_object,NROFMODULEII,NROFMODULEV)):-
%    active(new_object),
%    ooasp_isa(frame,new_object),
%    NROFMODULEII = #count { M:ooasp_assoc(C,frame_modules,new_object,M),ooasp_isa(moduleII,M) },
%    NROFMODULEV = #count { M:ooasp_assoc(C,frame_modules,new_object,M),ooasp_isa(moduleV,M) },
%    NROFMODULEII = 0,
%    NROFMODULEV > 0.

% new moduleII
%ooasp_cv(moduleII_requires_moduleV,F,"ModuleII requires moduleV in frame3 {} new_object {} {} {}",(F,new_object,NROFMODULEII,NROFMODULEV)):-
%    active(new_object),
%    ooasp_isa(frame,F),
%    ooasp_assoc(C,frame_modules,F,new_object),
%    ooasp_isa(moduleII,new_object),
%    NROFMODULEII = #count { M:ooasp_assoc(C,frame_modules,F,M),ooasp_isa(moduleII,M) },
%    NROFMODULEV = #count { M:ooasp_assoc(C,frame_modules,F,M),ooasp_isa(moduleV,M) },
%    NROFMODULEII > 0,
%    NROFMODULEV = 0.

%ooasp_cv(moduleII_requires_moduleV,F,"ModuleII requires moduleV in frame4 {} new_object {} {} {}",(F,new_object,NROFMODULEII,NROFMODULEV)):-
%    active(new_object),
%    ooasp_isa(frame,F),
%    ooasp_assoc(C,frame_modules,F,new_object),
%    ooasp_isa(moduleII,new_object),
%    NROFMODULEII = #count { M:ooasp_assoc(C,frame_modules,F,M),ooasp_isa(moduleII,M) },
%    NROFMODULEV = #count { M:ooasp_assoc(C,frame_modules,F,M),ooasp_isa(moduleV,M) },
%    NROFMODULEII = 0,
%    NROFMODULEV > 0.


% new moduleV
%ooasp_cv(moduleII_requires_moduleV,F,"ModuleII requires moduleV in frame5 {} new_object {} {} {}",(F,new_object,NROFMODULEII,NROFMODULEV)):-
%    active(new_object),
%    ooasp_isa(frame,F),
%    ooasp_assoc(C,frame_modules,F,new_object),
%    ooasp_isa(moduleV,new_object),
%    NROFMODULEII = #count { M:ooasp_assoc(C,frame_modules,F,M),ooasp_isa(moduleII,M) },
%    NROFMODULEV = #count { M:ooasp_assoc(C,frame_modules,F,M),ooasp_isa(moduleV,M) },
%    NROFMODULEII > 0,
%    NROFMODULEV = 0.

%ooasp_cv(moduleII_requires_moduleV,F,"ModuleII requires moduleV in frame6 {} new_object {} {} {}",(F,new_object,NROFMODULEII,NROFMODULEV)):-
%    active(new_object),
%    ooasp_isa(frame,F),
%    ooasp_assoc(C,frame_modules,F,new_object),
%    ooasp_isa(moduleV,new_object),
%    NROFMODULEII = #count { M:ooasp_assoc(C,frame_modules,F,M),ooasp_isa(moduleII,M) },
%    NROFMODULEV = #count { M:ooasp_assoc(C,frame_modules,F,M),ooasp_isa(moduleV,M) },
%    NROFMODULEII = 0,
%    NROFMODULEV > 0.


