% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT


#program domain(new_id).

{ ooasp_isa_leaf(CONFIG,LEAFCLASS,new_id):
		ooasp_leafclass(V,LEAFCLASS), 
  		ooasp_subclass(V,LEAFCLASS,C) } 1:- 
  	ooasp_configuration(V,CONFIG),
  	ooasp_domain(CONFIG,C,new_id),
	guess.

% % Associations from new_id
{ ooasp_associated(CONFIG,ASSOC,new_id,ID2) } :- 	
	ooasp_configuration(V,CONFIG),
	ooasp_assoc(V,ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),
	ooasp_isa(CONFIG,C1,new_id),
	ID2<new_id,
	ooasp_isa(CONFIG,C2,ID2),
	guess.

{ ooasp_associated(CONFIG,ASSOC,ID1,new_id)} :- 
	ooasp_configuration(V,CONFIG),
	ooasp_assoc(V,ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),
	ooasp_isa(CONFIG,C2,new_id),
	ID1<new_id,
	ooasp_isa(CONFIG,C1,ID1),
	guess.

% Attributes
1 { ooasp_attribute_value(CONFIG,N,new_id,VALUE):ooasp_attribute_enum(V,C,N,VALUE) } 1 :-
	ooasp_isa(CONFIG,C,new_id),
	ooasp_attribute(V,C,N,T),
	ooasp_attribute_hasdomain(V,C,N),
	ooasp_configuration(V,CONFIG),
	guess.

% TODO: this rule is only used if MAX-MIN < 30
1 { ooasp_attribute_value(CONFIG,ATTR,new_id,VALUE):VALUE=MIN..MAX } 1:-
	ooasp_attribute(V,C,ATTR,T),
	ooasp_isa(CONFIG,C,new_id),
	ooasp_attribute_minInclusive(V,C,ATTR,MIN),
	ooasp_attribute_maxInclusive(V,C,ATTR,MAX),
	%(MAX-MIN)<30,
	ooasp_configuration(V,CONFIG),
	guess.