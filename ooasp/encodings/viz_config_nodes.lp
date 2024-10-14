% Copyright (c) 2024 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

shown_association(assumed,Name,ID1,ID2):-ooasp_smallest_assoc(Name),_clinguin_assume(ooasp_associated(Name,ID1,ID2),true).
shown_association(browse,Name,ID1,ID2):-ooasp_smallest_assoc(Name), ooasp_associated(Name,ID1,ID2), _clinguin_browsing,  not _clinguin_assume(ooasp_associated(Name,ID1,ID2),true).
shown_association(infer,Name,ID1,ID2):-ooasp_smallest_assoc(Name),_all(ooasp_associated(Name,ID1,ID2)), not _clinguin_assume(ooasp_associated(Name,ID1,ID2),true), not _clinguin_browsing.

assumed_isa(C,ID) :- ooasp_domain(Class,ID), _all(ooasp_isa_leaf(C,ID)), _clinguin_assume(ooasp_isa(C,ID), true).
suggested_isa(C,ID) :- ooasp_domain(Class,ID), _all(ooasp_isa_leaf(C,ID)), not _clinguin_assume(ooasp_isa(C,ID), true), not _clinguin_browsing.
browse_isa(C,ID) :- ooasp_domain(Class,ID), ooasp_isa_leaf(C,ID), not _clinguin_assume(ooasp_isa(C,ID), true), _clinguin_browsing.

label_isa(C,ID):- assumed_isa(C,ID).
label_isa(C,ID):- suggested_isa(C,ID).
label_isa(C,ID):- browse_isa(C,ID).

any_node(Object_id) :- ooasp_domain(_,Object_id).
node(Object_id,config) :- ooasp_domain(_,Object_id).