% Copyright (c) 2024 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

#program domain(new_object, cls).

ooasp_potential_cv(moduleII_requires_moduleV).

% % moduleII requires moduleV
ooasp_cv(moduleII_requires_moduleV,F,"ModuleII requires moduleV in frame {}",(F,new_object)):-
	active(new_object),
    ooasp_isa(frame,F),
    ooasp_isa(moduleII,M),
    ooasp_associated(frame_modules,F,M),
    not ooasp_isa(moduleV,M5): ooasp_associated(frame_modules,F,M5).