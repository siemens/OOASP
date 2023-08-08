% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

% EXAMPLE racks
% classes
ooasp_class(object).

ooasp_class(rack).
ooasp_subclass(rack,object).

ooasp_class(rackSingle).
ooasp_subclass(rackSingle,rack).

ooasp_class(rackDouble).
ooasp_subclass(rackDouble,rack).

ooasp_class(frame).
ooasp_subclass(frame,object).

ooasp_class(element).
ooasp_class(elementA).
ooasp_class(elementB).
ooasp_class(elementC).
ooasp_class(elementD).
ooasp_subclass(element,object).
ooasp_subclass(elementA,element).
ooasp_subclass(elementB,element).
ooasp_subclass(elementC,element).
ooasp_subclass(elementD,element).

ooasp_class(module).
ooasp_class(moduleI).
ooasp_class(moduleII).
ooasp_class(moduleIII).
ooasp_class(moduleIV).
ooasp_class(moduleV).
ooasp_subclass(module,object).
ooasp_subclass(moduleI,module).
ooasp_subclass(moduleII,module).
ooasp_subclass(moduleIII,module).
ooasp_subclass(moduleIV,module).
ooasp_subclass(moduleV,module).

% associations
% -1 means * i.e. unrestricted

ooasp_assoc(rack_frames,rack,1,1,frame,4,8).
ooasp_assoc(frame_modules,frame,1,1,module,0,5).
ooasp_assoc(element_modules,element,0,1,module,1,4).

ooasp_attr(frame,frame_position,int).
ooasp_attr_minInclusive(frame,frame_position,1).
ooasp_attr_maxInclusive(frame,frame_position,8).

