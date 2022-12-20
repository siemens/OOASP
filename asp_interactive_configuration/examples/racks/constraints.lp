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

ooasp_partial_cv(customlowerbound).
ooasp_partial_cv(racksinglelowerbound).
ooasp_partial_cv(rackdoublelowerbound).
ooasp_partial_cv(module_requires_element).
ooasp_partial_cv(moduleII_requires_moduleV).

#program domain(new_id).


ooasp_cv(C,assoc1_constraint1,new_id,"Asssociated by {} to {} which is not of type {}",(new_id,ASSOC,ID2,C2)) :- 
    ooasp_associated(C,ASSOC,new_id,ID2),
    assoc1_constraint(ASSOC,C1,CARD,C2),
    ooasp_isa(C,C1,new_id),
    not ooasp_isa(C,C2,ID2).

ooasp_cv(C,assoc1_constraint1,new_id,"Asssociated by {} to {} which is not of type {}",(new_id,ASSOC,ID2,C2)) :- 
    ooasp_associated(C,ASSOC,new_id,ID2),
    assoc1_constraint(ASSOC,C1,CARD,C2),
    not ooasp_isa(C,C1,new_id),
    ooasp_isa(C,C2,ID2).

ooasp_cv(C,assoc1_constraint2,new_id,"Asssociated by {} to {} which is not of type {}",(new_id,ASSOC,ID1,C1)) :- 
    ooasp_associated(C,ASSOC,ID1,new_id),
    assoc1_constraint(ASSOC,C1,CARD,C2),
    not ooasp_isa(C,C1,ID1),
    ooasp_isa(C,C2,new_id).

ooasp_cv(C,assoc1_constraint2,new_id,"Asssociated by {} to {} which is not of type {}",(new_id,ASSOC,ID1,C1)) :- 
    ooasp_associated(C,ASSOC,ID1,new_id),
    assoc1_constraint(ASSOC,C1,CARD,C2),
    ooasp_isa(C,C1,ID1),
    not ooasp_isa(C,C2,new_id).

ooasp_cv(C,customlowerbound,ID,"Custom lowerbound for association {} not reached: {}",(ASSOC,CARD,new_id)):-
    #count { ID2:ooasp_associated_general(CONFIG,ASSOC,1,ID,ID2) } < CARD,
    ooasp_isa(C,C1,ID),
    assoc1_constraint(ASSOC,C1,CARD,C2),
	active(new_id).

ooasp_cv(C,customupperbound,ID,"Custom upperbound for association {} not reached: {}",(ASSOC,CARD,new_id)):-
    #count { ID2:ooasp_associated_general(CONFIG,ASSOC,1,ID,ID2) } > CARD,
    assoc1_constraint(ASSOC,C1,CARD,C2),
    ooasp_isa(C,C1,ID),
	active(new_id).


% rack_frames
ooasp_cv(C,racksinglelowerbound,ID,"Rack singles should be associated to 4 frames ",(new_id,)) :- 
    ooasp_isa(C,rackSingle,ID), 
    #count { ID2:ooasp_associated_general(CONFIG,ASSOC,1,ID,ID2) } < 4,
	active(new_id).

ooasp_cv(C,racksingleupperbound,ID,"Rack singles should be associated to 4 frames ",(new_id,)) :- 
    ooasp_isa(C,rackSingle,ID), 
    #count { ID2:ooasp_associated_general(CONFIG,ASSOC,1,ID,ID2) } > 4,
	active(new_id).


ooasp_cv(C,rackdoublelowerbound,ID,"Rack doubles should be associated to 8 frames ",(new_id,)) :- 
    ooasp_isa(C,rackDouble,ID), 
    #count { ID2:ooasp_associated_general(CONFIG,ASSOC,1,ID,ID2) } < 8,
	active(new_id).

ooasp_cv(C,rackdoubleupperbound,ID,"Rack doubles should be associated to 8 frames ",(new_id,)) :- 
    ooasp_isa(C,rackDouble,ID), 
    #count { ID2:ooasp_associated_general(CONFIG,ASSOC,1,ID,ID2) } > 8,
	active(new_id).


ooasp_cv(C,module_requires_element,ID,"Modules of type {} must have at least one element",(LEAFCLASS,new_id)) :-
    #count { ID2:ooasp_associated_general(CONFIG,element_modules,2,ID,ID2) } == 0,
	active(new_id),
    ooasp_isa(C,module,ID),
    ooasp_isa_leaf(C,LEAFCLASS,ID),
    LEAFCLASS != moduleV.


ooasp_cv(C,module_requires_element,ID,"Modules of type {} must have at least one element",(LEAFCLASS,new_id)) :- 
	ooasp_arity(C,element_modules, 2, ID, ARITY, new_id),
	active(new_id),
    ooasp_isa(C,module,ID),
    ooasp_isa_leaf(C,LEAFCLASS,ID),
    LEAFCLASS != moduleV,
    ARITY==0.

ooasp_cv(C,frame_position_must_be_unique, new_id, "Frame position is equal to the one of frame {} ",(F,)):-
    ooasp_associated(C,rack_frames,R,new_id),
    ooasp_associated(C,rack_frames,R,F),
    new_id!=F, 
    ooasp_attribute_value(C,frame_position,new_id,P),
    ooasp_attribute_value(C,frame_position,F,P).

ooasp_cv(C,frame_position_must_be_unique, F1, "Frame position is equal to the one of frame {} ",(F2,new_id)):-
    ooasp_associated(C,rack_frames,new_id,F1),
    ooasp_associated(C,rack_frames,new_id,F2),
    F1!=F2, 
    ooasp_attribute_value(C,frame_position,F1,P),
    ooasp_attribute_value(C,frame_position,F2,P).

% frame positions for racksingle
ooasp_cv(C,frame_must_be_within_range, new_id, "Frame position is outside of range {} ",(new_id,)):-
    ooasp_isa(C,rackSingle,ID),
    ooasp_associated(C,rack_frames,ID,new_id),
    ooasp_attribute_value(C,frame_position,F,P),
    P<1.

ooasp_cv(C,frame_must_be_within_range, new_id, "Frame position is outside of range {} ",(new_id,)):-
    ooasp_isa(C,rackSingle,ID),
    ooasp_associated(C,rack_frames,ID,new_id),
    ooasp_attribute_value(C,frame_position,F,P),
    P>4.

ooasp_cv(C,frame_must_be_within_range, F, "Frame position is outside of range {} ",(F,new_id)):-
    ooasp_isa(C,rackSingle,new_id),
    ooasp_associated(C,rack_frames,new_id,F),
    ooasp_attribute_value(C,frame_position,F,P),
    P<1.

ooasp_cv(C,frame_must_be_within_range, F, "Frame position is outside of range {} ",(F,new_id)):-
    ooasp_isa(C,rackSingle,new_id),
    ooasp_associated(C,rack_frames,new_id,F),
    ooasp_attribute_value(C,frame_position,F,P),
    P>4.

% frame positions for rackdouble
ooasp_cv(C,frame_must_be_within_range, new_id, "Frame position is outside of range {} ",(new_id,)):-
    ooasp_isa(C,rackDouble,ID),
    ooasp_associated(C,rack_frames,ID,new_id),
    ooasp_attribute_value(C,frame_position,F,P),
    P<1.

ooasp_cv(C,frame_must_be_within_range, new_id, "Frame position is outside of range {} ",(new_id,)):-
    ooasp_isa(C,rackDouble,ID),
    ooasp_associated(C,rack_frames,ID,new_id),
    ooasp_attribute_value(C,frame_position,F,P),
    P>8.

ooasp_cv(C,frame_must_be_within_range, F, "Frame position is outside of range {} ",(F,new_id)):-
    ooasp_isa(C,rackDouble,new_id),
    ooasp_associated(C,rack_frames,new_id,F),
    ooasp_attribute_value(C,frame_position,F,P),
    P<1.

ooasp_cv(C,frame_must_be_within_range, F, "Frame position is outside of range {} ",(F,new_id)):-
    ooasp_isa(C,rackDouble,new_id),
    ooasp_associated(C,rack_frames,new_id,F),
    ooasp_attribute_value(C,frame_position,F,P),
    P>8.

% moduleII requires moduleV
% TODO: Is using active(new_id) enough?
ooasp_cv(C,moduleII_requires_moduleV,F,"ModuleII requires moduleV in frame {} new_id {} {} {}",(F,new_id,NROFMODULEII,NROFMODULEV)):-
    active(new_id),
    ooasp_isa(C,frame,F),
    NROFMODULEII = #count { M:ooasp_associated(C,frame_modules,F,M),ooasp_isa(C,moduleII,M) },
    NROFMODULEV = #count { M:ooasp_associated(C,frame_modules,F,M),ooasp_isa(C,moduleV,M) },
    NROFMODULEII > 0,
    NROFMODULEV = 0.

ooasp_cv(C,moduleII_requires_moduleV,F,"ModuleII requires moduleV in frame {} new_id {} {} {}",(F,new_id,NROFMODULEII,NROFMODULEV)):-
    active(new_id),
    ooasp_isa(C,frame,F),
    NROFMODULEII = #count { M:ooasp_associated(C,frame_modules,F,M),ooasp_isa(C,moduleII,M) },
    NROFMODULEV = #count { M:ooasp_associated(C,frame_modules,F,M),ooasp_isa(C,moduleV,M) },
    NROFMODULEII = 0,
    NROFMODULEV > 0.

% new frame
%ooasp_cv(C,moduleII_requires_moduleV,new_id,"ModuleII requires moduleV in frame1 {} new_id {} {} {}",(new_id,new_id,NROFMODULEII,NROFMODULEV)):-
%    active(new_id),
%    ooasp_isa(C,frame,new_id),
%    NROFMODULEII = #count { M:ooasp_associated(C,frame_modules,new_id,M),ooasp_isa(C,moduleII,M) },
%    NROFMODULEV = #count { M:ooasp_associated(C,frame_modules,new_id,M),ooasp_isa(C,moduleV,M) },
%    NROFMODULEII > 0,
%    NROFMODULEV = 0.

%ooasp_cv(C,moduleII_requires_moduleV,new_id,"ModuleII requires moduleV in frame2 {} new_id {} {} {}",(new_id,new_id,NROFMODULEII,NROFMODULEV)):-
%    active(new_id),
%    ooasp_isa(C,frame,new_id),
%    NROFMODULEII = #count { M:ooasp_associated(C,frame_modules,new_id,M),ooasp_isa(C,moduleII,M) },
%    NROFMODULEV = #count { M:ooasp_associated(C,frame_modules,new_id,M),ooasp_isa(C,moduleV,M) },
%    NROFMODULEII = 0,
%    NROFMODULEV > 0.

% new moduleII
%ooasp_cv(C,moduleII_requires_moduleV,F,"ModuleII requires moduleV in frame3 {} new_id {} {} {}",(F,new_id,NROFMODULEII,NROFMODULEV)):-
%    active(new_id),
%    ooasp_isa(C,frame,F),
%    ooasp_associated(C,frame_modules,F,new_id),
%    ooasp_isa(C,moduleII,new_id),
%    NROFMODULEII = #count { M:ooasp_associated(C,frame_modules,F,M),ooasp_isa(C,moduleII,M) },
%    NROFMODULEV = #count { M:ooasp_associated(C,frame_modules,F,M),ooasp_isa(C,moduleV,M) },
%    NROFMODULEII > 0,
%    NROFMODULEV = 0.

%ooasp_cv(C,moduleII_requires_moduleV,F,"ModuleII requires moduleV in frame4 {} new_id {} {} {}",(F,new_id,NROFMODULEII,NROFMODULEV)):-
%    active(new_id),
%    ooasp_isa(C,frame,F),
%    ooasp_associated(C,frame_modules,F,new_id),
%    ooasp_isa(C,moduleII,new_id),
%    NROFMODULEII = #count { M:ooasp_associated(C,frame_modules,F,M),ooasp_isa(C,moduleII,M) },
%    NROFMODULEV = #count { M:ooasp_associated(C,frame_modules,F,M),ooasp_isa(C,moduleV,M) },
%    NROFMODULEII = 0,
%    NROFMODULEV > 0.


% new moduleV
%ooasp_cv(C,moduleII_requires_moduleV,F,"ModuleII requires moduleV in frame5 {} new_id {} {} {}",(F,new_id,NROFMODULEII,NROFMODULEV)):-
%    active(new_id),
%    ooasp_isa(C,frame,F),
%    ooasp_associated(C,frame_modules,F,new_id),
%    ooasp_isa(C,moduleV,new_id),
%    NROFMODULEII = #count { M:ooasp_associated(C,frame_modules,F,M),ooasp_isa(C,moduleII,M) },
%    NROFMODULEV = #count { M:ooasp_associated(C,frame_modules,F,M),ooasp_isa(C,moduleV,M) },
%    NROFMODULEII > 0,
%    NROFMODULEV = 0.

%ooasp_cv(C,moduleII_requires_moduleV,F,"ModuleII requires moduleV in frame6 {} new_id {} {} {}",(F,new_id,NROFMODULEII,NROFMODULEV)):-
%    active(new_id),
%    ooasp_isa(C,frame,F),
%    ooasp_associated(C,frame_modules,F,new_id),
%    ooasp_isa(C,moduleV,new_id),
%    NROFMODULEII = #count { M:ooasp_associated(C,frame_modules,F,M),ooasp_isa(C,moduleII,M) },
%    NROFMODULEV = #count { M:ooasp_associated(C,frame_modules,F,M),ooasp_isa(C,moduleV,M) },
%    NROFMODULEII = 0,
%    NROFMODULEV > 0.


