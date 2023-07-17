% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

% EXAMPLE racks
ooasp_kb(racks_v1).

% classes
ooasp_class(racks_v1,object).

ooasp_class(racks_v1,rack).
ooasp_subclass(racks_v1,rack,object).

ooasp_class(racks_v1,rackSingle).
ooasp_subclass(racks_v1,rackSingle,rack).

ooasp_class(racks_v1,rackDouble).
ooasp_subclass(racks_v1,rackDouble,rack).

ooasp_class(racks_v1,frame).
ooasp_subclass(racks_v1,frame,object).

ooasp_class(racks_v1,element).
ooasp_class(racks_v1,elementA).
ooasp_class(racks_v1,elementB).
ooasp_class(racks_v1,elementC).
ooasp_class(racks_v1,elementD).
ooasp_subclass(racks_v1,element,object).
ooasp_subclass(racks_v1,elementA,element).
ooasp_subclass(racks_v1,elementB,element).
ooasp_subclass(racks_v1,elementC,element).
ooasp_subclass(racks_v1,elementD,element).

ooasp_class(racks_v1,module).
ooasp_class(racks_v1,moduleI).
ooasp_class(racks_v1,moduleII).
ooasp_class(racks_v1,moduleIII).
ooasp_class(racks_v1,moduleIV).
ooasp_class(racks_v1,moduleV).
ooasp_subclass(racks_v1,module,object).
ooasp_subclass(racks_v1,moduleI,module).
ooasp_subclass(racks_v1,moduleII,module).
ooasp_subclass(racks_v1,moduleIII,module).
ooasp_subclass(racks_v1,moduleIV,module).
ooasp_subclass(racks_v1,moduleV,module).

% associations
% -1 means * i.e. unrestricted

ooasp_assoc(racks_v1,rack_frames,rack,1,1,frame,4,8).
ooasp_assoc(racks_v1,frame_modules,frame,1,1,module,0,5).
ooasp_assoc(racks_v1,element_modules,element,0,1,module,1,4).

ooasp_attribute(racks_v1,frame,frame_position,int).
ooasp_attribute_minInclusive(racks_v1,frame,frame_position,1).
ooasp_attribute_maxInclusive(racks_v1,frame,frame_position,8).

