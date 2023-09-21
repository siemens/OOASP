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


% :- ooasp_isa_leaf(C1,new_object), % Instanciates new_object
%       ooasp_isa_leaf(C2,ID1), 
%       ooasp_isa_leaf(C2,ID2), 
%       ooasp_associated(A, new_object, ID1),
%       not user(ooasp_associated(A, new_object, ID1)),
%       ooasp_associated(A, new_object, ID2),
%       not user(ooasp_associated(A, new_object, ID2)),
%       ID1<ID2.


% :- ooasp_isa_leaf(C2,new_object), % Instanciates new_object
%       ooasp_isa_leaf(C1,ID1),
%       ooasp_isa_leaf(C2,ID2), 
%       ooasp_associated(A, ID1, new_object),
%       not user(ooasp_associated(A, ID1, new_object)),
      
      
%       not ooasp_associated(A, ID1, ID2),
%       user(ooasp_associated(A, ID1, ID2)),
%       new_object>ID2.