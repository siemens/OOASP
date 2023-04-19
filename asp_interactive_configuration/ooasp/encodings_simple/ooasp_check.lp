% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

#program domain(new_id).

:- ooasp_cv(NAME,_,_,_),
	not ooasp_partial_cv(NAME),
	check.
:- ooasp_cv(NAME,_,_,_),
	ooasp_partial_cv(NAME),
	check_partial_cv,
	check.

ooasp_partial_cv(lowerbound).
ooasp_partial_cv(no_value).

% ooasp_cv(NAME,OBEJCT,STR,ARGS)
%=======================================
% Instances
%=======================================

% ------ (USER INPUT) Cant be instance of two different leaf classes

ooasp_cv(notinstanceofsubclass,new_id,"Has two leaf classes {} and {}",(C1,C2)) :-
	ooasp_isa_leaf(C1,new_id),
	ooasp_isa_leaf(C2,new_id),
	C1<C2.

%=======================================
% Associations
%=======================================


%--- Association bounds

ooasp_cv(upperbound,ID1,
  "Upperbound for association {} exceeded: {}",
  (A,CMAX,new_id)):-
	ooasp_assoc_limit(A,max,OPT,C,CMAX),
	ooasp_isa(C,ID1),
	#count{ID2:ooasp_ass_gen(A,OPT,ID1,ID2)}
		> CMAX,
	active(new_id).


ooasp_cv(lowerbound,ID1,"Lowerbound for association {} not reached: {}",(ASSOC,CMIN,new_id)):-
	ooasp_assoc_limit(ASSOC,min,OPT,C,CMIN),
	ooasp_isa(C,ID1),
	#count { ID2:ooasp_ass_gen(ASSOC,OPT,ID1,ID2) } < CMIN,
	active(new_id).


%--- Associations are only allowed to something instantiated

ooasp_cv(no_instance_for_association,new_id,"Associated by {} to {} but not is not instantiated",(ASSOC,ID2)) :-
	ooasp_associated(ASSOC,new_id,ID2),
	not ooasp_isa(_,new_id).

ooasp_cv(no_instance_for_association,new_id,"Associated by {} to {} but not instantiated",(ASSOC,ID1)) :-
	ooasp_associated(ASSOC,ID1,new_id),
	not ooasp_isa(_,new_id).

ooasp_cv(no_instance_for_association,new_id,"Associated by {} to {} which is not instantiated",(ASSOC,ID2)) :-
	ooasp_associated(ASSOC,new_id,ID2),
	not ooasp_isa(_,ID2).

ooasp_cv(no_instance_for_association,new_id,"Associated by {} to {} which is not instantiated",(ASSOC,ID1)) :-
	ooasp_associated(ASSOC,ID1,new_id),
	not ooasp_isa(_,ID1).


%--- (USER INPUT) Type of association

ooasp_cv(wrongtypeinassoc,new_id,"Associated by {} but is not of class {}",(ASSOC,C1)) :-
	ooasp_associated(ASSOC,new_id,_),
	ooasp_assoc(ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),
	not ooasp_isa(C1,new_id).

ooasp_cv(wrongtypeinassoc,new_id,"Associated by {} but is not of class {}",(ASSOC,C2)) :-
	ooasp_associated(ASSOC,_,new_id),
	ooasp_assoc(ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),
	not ooasp_isa(C2,new_id).


%=======================================
% Values
%=======================================

%--- (USER INPUT) Attribute value must belong to instance class

ooasp_cv(no_instance_for_attribute,new_id,"Attribute {} not of selected class",(ATTR,)) :-
	ooasp_attr(C1,ATTR,T),
	ooasp_attr_value(ATTR,new_id,VALUE),
	not ooasp_isa(C1,new_id).

%--- (USER INPUT) Attribute value must belong to instance

ooasp_cv(no_instance_for_attribute,new_id,"Value for {} assigned but instanciated",(ATTR,)) :-
	ooasp_attr_value(ATTR,new_id,VALUE),
	not ooasp_isa(_,new_id).

%--- (USER INPUT) Missing atribute value
ooasp_cv(no_value,new_id,"Missing value for {}",(ATTR,)) :-
	 ooasp_attr(C,ATTR,T),
	 ooasp_attr_hasdomain(C,ATTR),
	 ooasp_isa(C,new_id),
	 not ooasp_attr_value(ATTR,new_id,_).

%--- (USER INPUT) Atribute value not from domain
ooasp_cv(value_not_domain,new_id,"Value {} for {} not from domain",(VALUE,ATTR)) :-
	 ooasp_attr(C,ATTR,T),
	 ooasp_attr_hasdomain(C,ATTR),
	 ooasp_isa(C,new_id),
	 ooasp_attr_value(ATTR,new_id,VALUE),
	 not ooasp_attr_enum(C,ATTR,VALUE).

%--- (USER INPUT) Multiple values for a value
ooasp_cv(conflicting_values,new_id,"Multiple values for {}: {},{}",(ATTR,V1,V2)) :-
	 ooasp_attr(C,ATTR,T),
	 ooasp_attr_value(ATTR,new_id,V1),
	 ooasp_attr_value(ATTR,new_id,V2),
	 V1<V2.

%--- (USER INPUT) Value outside range
ooasp_cv(value_outside_of_range,new_id,"Value for {} outside range {}<{}",(ATTR,VALUE,MIN)) :-
	 ooasp_attr(C,ATTR,T),
	 ooasp_isa(C,new_id),
	 ooasp_attr_value(ATTR,new_id,VALUE),
	 ooasp_attr_minInclusive(C,ATTR,MIN),
	 VALUE<MIN.

ooasp_cv(value_outside_of_range,new_id,"Value for {} outside range {}>{}",(ATTR,VALUE,MAX)) :-
	 ooasp_attr(C,ATTR,T),
	 ooasp_isa(C,new_id),
	 ooasp_attr_value(ATTR,new_id,VALUE),
	 ooasp_attr_maxInclusive(C,ATTR,MAX),
	 VALUE>MAX.

