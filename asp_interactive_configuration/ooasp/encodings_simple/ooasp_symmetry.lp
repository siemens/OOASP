% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

#program domain(new_object).

:- ooasp_isa_leaf(C1,new_object),
      ooasp_isa_leaf(C2,ID),
      ID<new_object,
      C1<C2,
      not user(ooasp_isa_leaf(C1,new_object)),
      not user(ooasp_isa_leaf(C2,ID)).

:- ooasp_isa_leaf(_,new_object),
      not ooasp_isa_leaf(_,ID),
      ooasp_isa(_,ID),
      ID<new_object.