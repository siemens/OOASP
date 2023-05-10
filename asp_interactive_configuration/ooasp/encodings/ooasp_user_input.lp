% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

#program domain(new_object).

%--------
%  Externals for user selections to allow checks of partial configurations
%--------
#external user(ooasp_isa_leaf(CONFIG,LEAFCLASS,new_object)):
	ooasp_configuration(V,CONFIG),
	ooasp_leafclass(V,LEAFCLASS),
	ooasp_domain(CONFIG,C,new_object),
	ooasp_subclass(V,LEAFCLASS,C),
	not ignore_externals.

#external user(ooasp_associated(CONFIG,ASSOC,new_object,ID2)):
	ooasp_configuration(V,CONFIG),
	ooasp_domain(CONFIG,C,ID2),
	ooasp_assoc(V,ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),
	not ignore_externals.

#external user(ooasp_associated(CONFIG,ASSOC,ID1,new_object)):
	ooasp_configuration(V,CONFIG),
	ooasp_domain(CONFIG,C,ID1),
	ooasp_assoc(V,ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),
	not ignore_externals.

#external user(ooasp_attribute_value(CONFIG,N,new_object,VALUE)):
	ooasp_configuration(V,CONFIG),
	ooasp_attribute_enum(V,C,N,VALUE),
	ooasp_attribute(V,C,N,T),
	not ignore_externals.

ooasp_isa_leaf(CONFIG,LEAFCLASS,new_object) :- user(ooasp_isa_leaf(CONFIG,LEAFCLASS,new_object)).
ooasp_associated(CONFIG,ASSOC,new_object,ID2) :- user(ooasp_associated(CONFIG,ASSOC,new_object,ID2)).
ooasp_associated(CONFIG,ASSOC,ID1,new_object) :- user(ooasp_associated(CONFIG,ASSOC,ID1,new_object)).
ooasp_attribute_value(CONFIG,N,new_object,VALUE) :- user(ooasp_attribute_value(CONFIG,N,new_object,VALUE)).