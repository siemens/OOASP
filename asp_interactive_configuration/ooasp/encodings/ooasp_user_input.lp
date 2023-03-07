% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

#program domain(new_id).

%--------
%  Externals for user selections to allow checks of partial rations
%--------
#external user(ooasp_isa_leaf(LEAFCLASS,new_id)):
	ooasp_leafclass(V,LEAFCLASS),
	ooasp_domain(C,new_id),
	ooasp_subclass(V,LEAFCLASS,C),
	not ignore_externals.

#external user(ooasp_associated(ASSOC,new_id,ID2)):
	ooasp_domain(C,ID2),
	ooasp_assoc(V,ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),
	not ignore_externals.

#external user(ooasp_associated(ASSOC,ID1,new_id)):
	ooasp_domain(C,ID1),
	ooasp_assoc(V,ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),
	not ignore_externals.

#external user(ooasp_attribute_value(N,new_id,VALUE)):
	ooasp_attribute_enum(V,C,N,VALUE),
	ooasp_attribute(V,C,N,T),
	not ignore_externals.

ooasp_isa_leaf(LEAFCLASS,new_id) :- user(ooasp_isa_leaf(LEAFCLASS,new_id)).
ooasp_associated(ASSOC,new_id,ID2) :- user(ooasp_associated(ASSOC,new_id,ID2)).
ooasp_associated(ASSOC,ID1,new_id) :- user(ooasp_associated(ASSOC,ID1,new_id)).
ooasp_attribute_value(N,new_id,VALUE) :- user(ooasp_attribute_value(N,new_id,VALUE)).