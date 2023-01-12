% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

#program domain(new_id).

:- ooasp_isa_leaf(CONFIG,LEAFCLASS_1,new_id), %Assigned
   ooasp_isa_leaf(CONFIG,LEAFCLASS_2,ID),
   ID<new_id, %Different 
   LEAFCLASS_1<LEAFCLASS_2,
   not user(ooasp_isa_leaf(CONFIG,LEAFCLASS_1,new_id)), %Not selected
   not user(ooasp_isa_leaf(CONFIG,LEAFCLASS_2,ID)),
   use_symmetry.

:- ooasp_isa_leaf(CONFIG,_,new_id), %Assigned
   not ooasp_isa_leaf(CONFIG,_,ID),
   ooasp_isa(CONFIG,_,ID),
   ID<new_id,
   use_symmetry. %Different 