% Copyright (c) 2022-2024 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

:- ooasp_isa_leaf(C1,OBJECT),
      ooasp_isa_leaf(C2,ID),
      ID<OBJECT,
      C1<C2,
      ooasp_domain(object,OBJECT),
      ooasp_domain(object,ID),
      not user(ooasp_isa(_,OBJECT)),
      not user(ooasp_isa(_,ID)).

:- ooasp_isa_leaf(_,OBJECT), % Instanciates OBJECT
      not user(ooasp_isa(_,OBJECT)), % By choice
      ooasp_domain(object,OBJECT), % When There was a previous object
      ooasp_domain(object,ID),
      not ooasp_isa_leaf(_,ID), % That was not instanciated
      ID<OBJECT.
