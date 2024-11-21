% Copyright (c) 2022-2024 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

%--------
%  Externals for user selections to allow checks of partial rations
%--------

% ---- Classes
ooasp_isa(C,OBJECT) :-
	user(ooasp_isa(C,OBJECT)).

% ---- Associations
ooasp_associated(AS,OBJECT,ID2) :-
	user(ooasp_associated(AS,OBJECT,ID2)).
ooasp_associated(AS,ID1,OBJECT) :-
	user(ooasp_associated(AS,ID1,OBJECT)).

% ---- Attribute values
ooasp_attr_value(A,OBJECT,V) :-
	user(ooasp_attr_value(A,OBJECT,V)).