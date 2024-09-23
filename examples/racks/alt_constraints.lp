% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

#program domain(new_object, cls).

ooasp_potential_cv(moduleII_requires_moduleV).

% Rack Single frames must have a position smaller than 4
ooasp_cv(frame_must_be_within_range, new_object, "Frame position is outside of range {} ",(new_object,)):-
    ooasp_isa(rackSingle,ID),
    ooasp_associated(rack_frames,ID,new_object),
    ooasp_attr_value(frame_position,new_object,P),
    P>4.

ooasp_cv(frame_must_be_within_range, F, "Frame position is outside of range {} ",(F,new_object)):-
    ooasp_isa(rackSingle,new_object),
    ooasp_associated(rack_frames,new_object,F),
    ooasp_attr_value(frame_position,F,P),
    P>4.

% % moduleII requires moduleV
ooasp_cv(moduleII_requires_moduleV,F,"ModuleII requires moduleV in frame {}",(F,new_object)):-
	active(new_object),
    ooasp_isa(frame,F),
    ooasp_isa(moduleII,M),
    ooasp_associated(frame_modules,F,M),
    not 1{ooasp_isa(moduleV,M5): ooasp_associated(frame_modules,F,M5)}1.