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

% constraints -----------------------------------------------------

% type check and cardinalities 
% TODO: find general solution
% assoc1_constraint(ASSOC,C1,CARD,C2)
% currently this means: In the ASSOC all elements of C1 are associated with exactly CARD of C2 and nothing else
% assoc1_constraint(element_modules,elementA,1,moduleI).
% assoc1_constraint(element_modules,elementB,2,moduleII).
% assoc1_constraint(element_modules,elementC,3,moduleIII).
% assoc1_constraint(element_modules,elementD,4,moduleIV).

% ooasp_cv(C,assoc1_constraint1(ASSOC,ID1)):-ooasp_associated(C,ASSOC,ID1,ID2),assoc1_constraint(ASSOC,C1,CARD,C2),ooasp_isa(C,C1,ID1),not ooasp_isa(C,C2,ID2).
% ooasp_cv(C,assoc1_constraint2(ASSOC,ID2)):-ooasp_associated(C,ASSOC,ID1,ID2),assoc1_constraint(ASSOC,C1,CARD,C2),not ooasp_isa(C,C1,ID1),ooasp_isa(C,C2,ID2).

% ooasp_cv(C,card_constraint1(ASSOC,ID1)):-ooasp_is_associated1_cardinality(C,ASSOC,ID1,N),assoc1_constraint(ASSOC,C1,CARD,C2),ooasp_isa(C,C1,ID1),N!=CARD.

% % rack_frames
% ooasp_cv(C,rackSingle_requires_4frames(ID1)):-ooasp_is_associated1_cardinality(C,rack_frames,ID1,N), ooasp_isa(C,rackSingle,ID1), N!=4.
% ooasp_cv(C,rackDouble_requires_8frames(ID1)):-ooasp_is_associated1_cardinality(C,rack_frames,ID1,N), ooasp_isa(C,rackDouble,ID1), N!=8.

% % modules (except moduleV) require elements

% ooasp_cv(C,module_requires_element(C,ID)):- ooasp_is_associated2_cardinality(C,element_modules,ID,0), not ooasp_isa(C,ID,moduleV).
% ooasp_cv(C,module_may_not_have_element(C,ID)):-ooasp_is_associated2_cardinality(C,element_modules,ID,N), N>0, ooasp_isa(C,moduleV,ID).

% ooasp_cv(C,frame_position_must_be_unique(C,F1,F2,P)):-
%     ooasp_associated(C,rack_frames,R,F1),
%     ooasp_associated(C,rack_frames,R,F2),
%     F1!=F2, 
%     ooasp_attribute_value(C,frame_position,F1,P),
%     ooasp_attribute_value(C,frame_position,F2,P).


