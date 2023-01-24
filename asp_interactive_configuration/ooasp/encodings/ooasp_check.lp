% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

#program domain(new_id).

:- ooasp_cv(CONFIG,NAME,_,_,_), 
	ooasp_configuration(_,CONFIG), 
	not ooasp_partial_cv(NAME), 
	check.
:- ooasp_cv(CONFIG,NAME,_,_,_), 
	ooasp_configuration(_,CONFIG), 
	ooasp_partial_cv(NAME), 
	check_partial_cv,
	check.

ooasp_partial_cv(lowerbound).
ooasp_partial_cv(no_value).

% ooasp_cv(CONFIG,NAME,OBEJCT,STR,ARGS)
%=======================================
% Instances
%=======================================

% ------ (USER INPUT) Cant be instance of two different leaf classes

ooasp_cv(CONFIG,notinstanceofsubclass,new_id,"Has two leaf classes {} and {}",(C1,C2)) :-
	ooasp_configuration(V,CONFIG),
	ooasp_isa_leaf(CONFIG,C1,new_id),
	ooasp_isa_leaf(CONFIG,C2,new_id),
	C1<C2.

%=======================================
% Associations
%=======================================


%--- Association bounds

ooasp_cv(CONFIG,upperbound,ID1,"Upperbound for association {} exceeded: {}",(ASSOC,CMAX,new_id)):-
	ooasp_configuration(V,CONFIG),
	ooasp_assoc_limit(V,ASSOC,max,OPT,C,CMAX),
	ooasp_isa(CONFIG,C,ID1),
	#count { ID2:ooasp_associated_general(CONFIG,ASSOC,OPT,ID1,ID2) } > CMAX,
	active(new_id).


ooasp_cv(CONFIG,lowerbound,ID1,"Lowerbound for association {} not reached: {}",(ASSOC,CMIN,new_id)):-
	ooasp_configuration(V,CONFIG),
	ooasp_assoc_limit(V,ASSOC,min,OPT,C,CMIN),
	ooasp_isa(CONFIG,C,ID1),
	#count { ID2:ooasp_associated_general(CONFIG,ASSOC,OPT,ID1,ID2) } < CMIN,
	active(new_id).


%--- Associations are only allowed to something instanciated

ooasp_cv(CONFIG,no_instance_for_association,new_id,"Associated by {} to {} but not is not instantiated",(ASSOC,ID2)) :- 
	ooasp_associated(CONFIG,ASSOC,new_id,ID2),
	not ooasp_isa(CONFIG,_,new_id).

ooasp_cv(CONFIG,no_instance_for_association,new_id,"Associated by {} to {} but not instantiated",(ASSOC,ID1)) :- 
	ooasp_associated(CONFIG,ASSOC,ID1,new_id),
	not ooasp_isa(CONFIG,_,new_id).

ooasp_cv(CONFIG,no_instance_for_association,new_id,"Associated by {} to {} which is not instantiated",(ASSOC,ID2)) :- 
	ooasp_associated(CONFIG,ASSOC,new_id,ID2),
	not ooasp_isa(CONFIG,_,ID2).

ooasp_cv(CONFIG,no_instance_for_association,new_id,"Associated by {} to {} which is not instantiated",(ASSOC,ID1)) :- 
	ooasp_associated(CONFIG,ASSOC,ID1,new_id),
	not ooasp_isa(CONFIG,_,ID1).


%--- (USER INPUT) Type of association 

ooasp_cv(CONFIG,wrongtypeinassoc,new_id,"Associated by {} but is not of class {}",(ASSOC,C1)) :-
	ooasp_configuration(V,CONFIG),
	ooasp_associated(CONFIG,ASSOC,new_id,_),
	ooasp_assoc(V,ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),
	not ooasp_isa(CONFIG,C1,new_id).

ooasp_cv(CONFIG,wrongtypeinassoc,new_id,"Associated by {} but is not of class {}",(ASSOC,C2)) :-
	ooasp_configuration(V,CONFIG),
	ooasp_associated(CONFIG,ASSOC,_,new_id),
	ooasp_assoc(V,ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),
	not ooasp_isa(CONFIG,C2,new_id).


%=======================================
% Values
%=======================================

%--- (USER INPUT) Attribute value must belong to instance class

ooasp_cv(CONFIG,no_instance_for_attribute,new_id,"Attribute {} not of selected class",(ATTR,)) :- 
	ooasp_attribute(V,C1,ATTR,T),
	ooasp_attribute_value(CONFIG,ATTR,new_id,VALUE),
	not ooasp_isa(CONFIG,C1,new_id).

%--- (USER INPUT) Attribute value must belong to instance

ooasp_cv(CONFIG,no_instance_for_attribute,new_id,"Value for {} assigned but instanciated",(ATTR,)) :- 
	ooasp_attribute_value(CONFIG,ATTR,new_id,VALUE),
	not ooasp_isa(CONFIG,_,new_id).

%--- (USER INPUT) Missing atribute value
ooasp_cv(CONFIG,no_value,new_id,"Missing value for {}",(ATTR,)) :- 
	 ooasp_configuration(V,CONFIG),
	 ooasp_attribute(V,C,ATTR,T),
	 ooasp_attribute_hasdomain(V,C,ATTR),
	 ooasp_isa(CONFIG,C,new_id),
	 not ooasp_attribute_value(CONFIG,ATTR,new_id,_).

%--- (USER INPUT) Atribute value not from domain
ooasp_cv(CONFIG,value_not_domain,new_id,"Value {} for {} not from domain",(VALUE,ATTR)) :- 
	 ooasp_configuration(V,CONFIG),
	 ooasp_attribute(V,C,ATTR,T),
	 ooasp_attribute_hasdomain(V,C,ATTR),
	 ooasp_isa(CONFIG,C,new_id),
	 ooasp_attribute_value(CONFIG,ATTR,new_id,VALUE),
	 not ooasp_attribute_enum(V,C,ATTR,VALUE).

%--- (USER INPUT) Multiple values for a value
ooasp_cv(CONFIG,conflicting_values,new_id,"Multiple values for {}: {},{}",(ATTR,V1,V2)) :- 
	 ooasp_configuration(V,CONFIG),
	 ooasp_attribute(V,C,ATTR,T),
	 ooasp_attribute_value(CONFIG,ATTR,new_id,V1),
	 ooasp_attribute_value(CONFIG,ATTR,new_id,V2),
	 V1<V2.

%--- (USER INPUT) Value outside range
ooasp_cv(CONFIG,value_outside_of_range,new_id,"Value for {} outside range {}<{}",(ATTR,VALUE,MIN)) :- 
	 ooasp_configuration(V,CONFIG),
	 ooasp_attribute(V,C,ATTR,T),
	 ooasp_isa(CONFIG,C,new_id),
	 ooasp_attribute_value(CONFIG,ATTR,new_id,VALUE),
	 ooasp_attribute_minInclusive(V,C,ATTR,MIN),
	 VALUE<MIN.

ooasp_cv(CONFIG,value_outside_of_range,new_id,"Value for {} outside range {}>{}",(ATTR,VALUE,MAX)) :-
	 ooasp_configuration(V,CONFIG),
	 ooasp_attribute(V,C,ATTR,T),
	 ooasp_isa(CONFIG,C,new_id),
	 ooasp_attribute_value(CONFIG,ATTR,new_id,VALUE),
	 ooasp_attribute_maxInclusive(V,C,ATTR,MAX),
	 VALUE>MAX.

