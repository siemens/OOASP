% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

#program domain(new_object, cls).

ooasp_cv(frame_position_must_be_unique, new_object, "Frame position is equal to the one of frame {} ",(F,)):-
    ooasp_associated(rack_frames,R,new_object),
    ooasp_associated(rack_frames,R,F),
    new_object!=F,
    ooasp_attr_value(frame_position,new_object,P),
    ooasp_attr_value(frame_position,F,P).

ooasp_cv(frame_position_must_be_unique, F1, "Frame position is equal to the one of frame {} ",(F2,new_object)):-
    ooasp_associated(rack_frames,new_object,F1),
    ooasp_associated(rack_frames,new_object,F2),
    F1!=F2,
    ooasp_attr_value(frame_position,F1,P),
    ooasp_attr_value(frame_position,F2,P).

% frame positions for racksingle
% Is this not part of the enumetation?
ooasp_cv(frame_must_be_within_range, new_object, "Frame position is outside of range {} ",(new_object,)):-
    ooasp_isa(rackSingle,ID),
    ooasp_associated(rack_frames,ID,new_object),
    ooasp_attr_value(frame_position,F,P),
    P<1.

ooasp_cv(frame_must_be_within_range, new_object, "Frame position is outside of range {} ",(new_object,)):-
    ooasp_isa(rackSingle,ID),
    ooasp_associated(rack_frames,ID,new_object),
    ooasp_attr_value(frame_position,F,P),
    P>4.

ooasp_cv(frame_must_be_within_range, F, "Frame position is outside of range {} ",(F,new_object)):-
    ooasp_isa(rackSingle,new_object),
    ooasp_associated(rack_frames,new_object,F),
    ooasp_attr_value(frame_position,F,P),
    P<1.

ooasp_cv(frame_must_be_within_range, F, "Frame position is outside of range {} ",(F,new_object)):-
    ooasp_isa(rackSingle,new_object),
    ooasp_associated(rack_frames,new_object,F),
    ooasp_attr_value(frame_position,F,P),
    P>4.

% frame positions for rackdouble
ooasp_cv(frame_must_be_within_range, new_object, "Frame position is outside of range {} ",(new_object,)):-
    ooasp_isa(rackDouble,ID),
    ooasp_associated(rack_frames,ID,new_object),
    ooasp_attr_value(frame_position,F,P),
    P<1.

ooasp_cv(frame_must_be_within_range, new_object, "Frame position is outside of range {} ",(new_object,)):-
    ooasp_isa(rackDouble,ID),
    ooasp_associated(rack_frames,ID,new_object),
    ooasp_attr_value(frame_position,F,P),
    P>8.

ooasp_cv(frame_must_be_within_range, F, "Frame position is outside of range {} ",(F,new_object)):-
    ooasp_isa(rackDouble,new_object),
    ooasp_associated(rack_frames,new_object,F),
    ooasp_attr_value(frame_position,F,P),
    P<1.

ooasp_cv(frame_must_be_within_range, F, "Frame position is outside of range {} ",(F,new_object)):-
    ooasp_isa(rackDouble,new_object),
    ooasp_associated(rack_frames,new_object,F),
    ooasp_attr_value(frame_position,F,P),
    P>8.

% moduleII requires moduleV
% TODO: Is using active(new_object) enough?
ooasp_cv(moduleII_requires_moduleV,F,"ModuleII requires moduleV in frame {}",(F,new_object)):-
	active(new_object),
    ooasp_isa(frame,F),
    ooasp_isa(moduleII,M),
    ooasp_associated(frame_modules,F,M),
    not ooasp_isa(moduleV,M5): ooasp_associated(frame_modules,F,M5).

% ooasp_cv(moduleII_requires_moduleV,F,"ModuleII requires moduleV in frame {}",(F,new_object)):-
% 	active(new_object),
%     ooasp_isa(frame,F),
%     ooasp_isa(moduleII,new_object),
%     ooasp_associated(frame_modules,F,new_object),
%     not ooasp_isa(moduleV,M5): ooasp_associated(frame_modules,new_object,M5).

% ooasp_cv(moduleII_requires_moduleV,new_object,"ModuleII requires moduleV in frame {}",(new_object,new_object)):-
% 	% active(new_object),
%     ooasp_isa(frame,new_object),
%     ooasp_isa(moduleII,M),
%     ooasp_associated(frame_modules,new_object,M),
%     not ooasp_isa(moduleV,M5): ooasp_associated(frame_modules,new_object,M5).
    
