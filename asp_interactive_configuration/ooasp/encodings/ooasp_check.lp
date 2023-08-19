% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

% ooasp_cv(NAME,OBEJCT,STR,ARGS)

#program domain(new_object, cls).

% Used to know the missing objects
:~ ooasp_cv(lowerbound,_,_,(ASSOC,CMIN,N,C,OPT,new_object)). [CMIN-N,ASSOC]

:- ooasp_cv(CV,_,_,_),
	not ooasp_potential_cv(CV),
	check_permanent_cv.
:- ooasp_cv(CV,_,_,_),
	ooasp_potential_cv(CV),
	check_potential_cv.

ooasp_potential_cv(lowerbound).
ooasp_potential_cv(no_value).

%=======================================
% Instances
%=======================================

% ------ (USER INPUT) Cant be instance of two different leaf classes
ooasp_cv(notinstanceofsubclass,new_object,"Has two leaf classes {} and {}",(C1,C2)) :-
	ooasp_isa_leaf(C1,new_object),
	ooasp_isa_leaf(C2,new_object),
	C1<C2.

%=======================================
% Associations
%=======================================


%--- Association bounds

ooasp_cv(upperbound,ID1,
  "Upperbound for {} exceeded: {}",
  (A,CMAX,new_object)):-
	ooasp_assoc_limit(A,max,OPT,C,CMAX,_),
	ooasp_isa(C,ID1),
	#count{ID2:ooasp_assoc_gen(A,OPT,ID1,ID2)}
		> CMAX,
	active(new_object).


lb_violation(lowerbound,ID1,"Lowerbound for {} is {} but has {} {}",(ASSOC,CMIN,N,C2,OPT,new_object)):-
	ooasp_assoc_limit(ASSOC,min,OPT,C,CMIN,C2),
	ooasp_isa(C,ID1),
	#count { ID2:ooasp_assoc_gen(ASSOC,OPT,ID1,ID2) } = N,
	N < CMIN,
	active(new_object).

ooasp_cv(lowerbound,ID1,M,(ASSOC,CMIN,N,C,OPT,new_object)):-
	lb_violation(lowerbound,ID1,M,(ASSOC,CMIN,N,C,OPT,new_object)),
	not lb_violation(lowerbound,ID1,_,(SUBASSOC,_,_,_,_,new_object)):ooasp_assoc_specialization(SUBASSOC,ASSOC).


%--- Associations are only allowed to something instantiated

ooasp_cv(no_instance_for_association,new_object,"Associated by {} to {} but not is not instantiated",(ASSOC,ID2)) :-
	ooasp_associated(ASSOC,new_object,ID2),
	not ooasp_isa(_,new_object).

ooasp_cv(no_instance_for_association,new_object,"Associated by {} to {} but not instantiated",(ASSOC,ID1)) :-
	ooasp_associated(ASSOC,ID1,new_object),
	not ooasp_isa(_,new_object).

ooasp_cv(no_instance_for_association,new_object,"Associated by {} to {} which is not instantiated",(ASSOC,ID2)) :-
	ooasp_associated(ASSOC,new_object,ID2),
	not ooasp_isa(_,ID2).

ooasp_cv(no_instance_for_association,new_object,"Associated by {} to {} which is not instantiated",(ASSOC,ID1)) :-
	ooasp_associated(ASSOC,ID1,new_object),
	not ooasp_isa(_,ID1).


%--- (USER INPUT) Type of association

ooasp_cv(wrongtypeinassoc,ID,"Associated by {} but is not of class {}",(ASSOC,C1,new_object)) :-
	active(new_object),
	ooasp_associated(ASSOC,ID,_),
	ooasp_assoc(ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),
	not ooasp_isa(C1,ID).

ooasp_cv(wrongtypeinassoc,ID,"Associated by {} but is not of class {}",(ASSOC,C2,new_object)) :-
	active(new_object),
	ooasp_associated(ASSOC,_,ID),
	ooasp_assoc(ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),
	not ooasp_isa(C2,ID).


%=======================================
% Values
%=======================================

%--- Unique attributes

% The class C of the main object is in position 1 

% The new object is of that class C
ooasp_cv(unique_attr, (new_object;ID1), "Attribute {} must be unique among all {}s associated by {} to {}",(ATTR,C,ASSOC,ID2,new_object )):-
	ooasp_unique_attr(ASSOC, C, ATTR),
	ooasp_assoc(ASSOC,C,_,_,_,_,_),
	ooasp_associated(ASSOC,new_object,ID2),
	ooasp_associated(ASSOC,ID1,ID2),
	new_object>ID1,
	ooasp_attr_value(ATTR,new_object,V),
	ooasp_attr_value(ATTR,ID1,V).

% The new object is of the other class
ooasp_cv(unique_attr, (ID3;ID1), "Attribute {} must be unique among all {}s associated by {} to {}",(ATTR,C,ASSOC,new_object)):-
	ooasp_unique_attr(ASSOC, C, ATTR),
	ooasp_assoc(ASSOC,C,_,_,_,_,_),
	ooasp_associated(ASSOC,ID3,new_object),
	ooasp_associated(ASSOC,ID1,new_object),
	ID3>ID1,
	ooasp_attr_value(ATTR,ID3,V),
	ooasp_attr_value(ATTR,ID1,V).

% The class C of the main object is in position 2 

ooasp_cv(unique_attr, (new_object;ID1), "Attribute {} must be unique among all {}s associated by {} to {}",(ATTR,C,ASSOC,ID2,new_object )):-
	ooasp_unique_attr(ASSOC, C, ATTR),
	ooasp_assoc(ASSOC,_,_,_,C,_,_),
	ooasp_associated(ASSOC,ID2,new_object),
	ooasp_associated(ASSOC,ID2,ID1),
	new_object>ID1,
	ooasp_attr_value(ATTR,new_object,V),
	ooasp_attr_value(ATTR,ID1,V).

ooasp_cv(unique_attr, (ID3;ID1), "Attribute {} must be unique among all {}s associated by {} to {}",(ATTR,C,ASSOC,new_object )):-
	ooasp_unique_attr(ASSOC, C, ATTR),
	ooasp_assoc(ASSOC,_,_,_,C,_,_),
	ooasp_associated(ASSOC,new_object,ID3),
	ooasp_associated(ASSOC,new_object,ID1),
	ID3>ID1,
	ooasp_attr_value(ATTR,ID3,V),
	ooasp_attr_value(ATTR,ID1,V).

%--- (USER INPUT) Attribute value must belong to instance class

ooasp_cv(no_instance_for_attribute,new_object,"Attribute {} not of selected class",(A,)) :-
	ooasp_attr(C1,A,T),
	ooasp_attr_value(A,new_object,V),
	not ooasp_isa(C1,new_object).

%--- (USER INPUT) Attribute value must belong to instance

ooasp_cv(no_instance_for_attribute,new_object,"Value for {} assigned but instanciated",(A,)) :-
	ooasp_attr_value(A,new_object,V),
	not ooasp_isa(_,new_object).

%--- (USER INPUT) Missing atribute value
ooasp_cv(no_value,new_object,"Missing value for {}",(A,)) :-
	 ooasp_attr(C,A,T),
	 ooasp_attr_enum(C,A,_),
	 ooasp_isa(C,new_object),
	 not ooasp_attr_value(A,new_object,_).

%--- (USER INPUT) Atribute value not from domain
ooasp_cv(value_not_domain,new_object,"Value {} for {} not from domain",(V,A)) :-
	 ooasp_attr(C,A,T),
	 ooasp_attr_enum(C,A,_),
	 ooasp_isa(C,new_object),
	 ooasp_attr_value(A,new_object,V),
	 not ooasp_attr_enum(C,A,V).

%--- (USER INPUT) Multiple values for a value
ooasp_cv(conflicting_values,new_object,"Multiple values for {}: {},{}",(A,V1,V2)) :-
	 ooasp_attr(C,A,T),
	 ooasp_attr_value(A,new_object,V1),
	 ooasp_attr_value(A,new_object,V2),
	 V1<V2.

%--- (USER INPUT) Value outside range
ooasp_cv(value_outside_of_range,new_object,"Value for {} outside range {}<{}",(A,V,MIN)) :-
	 ooasp_attr(C,A,T),
	 ooasp_isa(C,new_object),
	 ooasp_attr_value(A,new_object,V),
	 ooasp_attr_minInclusive(C,A,MIN),
	 V<MIN.

ooasp_cv(value_outside_of_range,new_object,"Value for {} outside range {}>{}",(A,V,MAX)) :-
	 ooasp_attr(C,A,T),
	 ooasp_isa(C,new_object),
	 ooasp_attr_value(A,new_object,V),
	 ooasp_attr_maxInclusive(C,A,MAX),
	 V>MAX.

