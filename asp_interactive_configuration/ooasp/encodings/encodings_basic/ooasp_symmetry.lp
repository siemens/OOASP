% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

#program domain(new_object).

:- ooasp_isa_leaf(CONFIG,LEAFCLASS_1,new_object), %Assigned
   ooasp_isa_leaf(CONFIG,LEAFCLASS_2,ID),
   ID<new_object, %Different
   LEAFCLASS_1<LEAFCLASS_2,
   not user(ooasp_isa_leaf(CONFIG,LEAFCLASS_1,new_object)), %Not selected
   not user(ooasp_isa_leaf(CONFIG,LEAFCLASS_2,ID)),
   use_symmetry.

:- ooasp_isa_leaf(CONFIG,_,new_object), %Assigned
   not ooasp_isa_leaf(CONFIG,_,ID),
   ooasp_isa(CONFIG,_,ID),
   ID<new_object,
   use_symmetry. %Different