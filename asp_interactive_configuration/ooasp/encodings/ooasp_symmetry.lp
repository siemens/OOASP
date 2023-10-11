% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

#program domain(new_object, cls).

:- ooasp_isa_leaf(C1,new_object),
      ooasp_isa_leaf(C2,ID),
      ID<new_object,
      C1<C2,
      ooasp_domain(object,new_object),
      ooasp_domain(object,ID),
      not user(ooasp_isa(_,new_object)),
      not user(ooasp_isa(_,ID)).

:- ooasp_isa_leaf(_,new_object), % Instanciates new_object
      not user(ooasp_isa(_,new_object)), % By choice
      ooasp_domain(object,new_object), % When There was a previous object
      ooasp_domain(object,ID),
      not ooasp_isa_leaf(_,ID), % That was not instanciated
      ID<new_object.
