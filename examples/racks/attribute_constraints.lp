% Copyright (c) 2024 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

#program domain(new_object, cls).

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