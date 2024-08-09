% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

#program domain(new_object, cls).

%-------------------------------------------------
% Symmetry breaking constraints to enforce an order in the classes of objects
% Enforces an order: C1, C2, C3, ... , Cn, None, None ... where C1 <= C2 <= C3 <= ... <= Cn
% It is only applyed to instantiend objects that where not user input
%-------------------------------------------------


:- ooasp_isa_leaf(C1,new_object),  % Instanciates the new new_object
      ooasp_isa_leaf(C2,new_object-1), % Instanciates the previous object
      C1<C2, % The class of the previous object is larger
      not user(ooasp_isa(_,new_object)), % By choice
      not user(ooasp_isa(_,new_object-1)). % By choice

:- ooasp_isa_leaf(_,new_object), % Instanciates new_object
      not user(ooasp_isa(_,new_object)), % By choice
      ooasp_domain(object,new_object),
      ooasp_domain(object,new_object-1), % When There was a previous object
      not ooasp_isa_leaf(_,new_object-1). % That was not instanciated
