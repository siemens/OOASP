% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

#program domain(new_id).

:- ooasp_isa_leaf(LEAFCLASS_1,new_id), %Assigned
   ooasp_isa_leaf(LEAFCLASS_2,ID),
   ID<new_id, %Different
   LEAFCLASS_1<LEAFCLASS_2,
   not user(ooasp_isa_leaf(LEAFCLASS_1,new_id)), %Not selected
   not user(ooasp_isa_leaf(LEAFCLASS_2,ID)),
   use_symmetry.

:- ooasp_isa_leaf(_,new_id), %Assigned
   not ooasp_isa_leaf(_,ID),
   ooasp_isa(_,ID),
   ID<new_id,
   use_symmetry. %Different