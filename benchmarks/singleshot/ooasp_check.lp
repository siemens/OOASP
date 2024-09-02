% Copyright (c) 2022-2024 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

% Integrity constraints for constraint violations, activated based on the externals
:- ooasp_cv(CV,_,_,_),
	not ooasp_potential_cv(CV),
	check_permanent_cv.
:- ooasp_cv(CV,_,_,_),
	ooasp_potential_cv(CV),
	check_potential_cv.

%=======================================
% Potential constraint violations
%=======================================

ooasp_potential_cv(lowerbound).
ooasp_potential_cv(no_value).

%=======================================
% Instances
%=======================================

% ------ (USER INPUT) Cant be instance of two different leaf classes
ooasp_cv(notinstanceofsubclass,OBJECT,"Has two leaf classes {} and {}",(C1,C2)) :-
	ooasp_isa_leaf(C1,OBJECT),
	ooasp_isa_leaf(C2,OBJECT),
	C1<C2.

%=======================================
% Associations
%=======================================

%--- Association bounds

ooasp_cv(upperbound,ID1,
  "Upperbound for {} exceeded: {}",
  (A,CMAX)):-
	ooasp_assoc_limit(A,max,OPT,C,CMAX,_),
	ooasp_isa(C,ID1),
	#count{ID2:ooasp_assoc_gen(A,OPT,ID1,ID2)}
		> CMAX.
	%active(OBJECT).

 % SAFETY VIOLATIONS
lb_violation(lowerbound,ID1,"Lowerbound for {} is {} but has {} {}",(ASSOC,CMIN,N,C2,OPT)):-
	ooasp_assoc_limit(ASSOC,min,OPT,C,CMIN,C2),
	ooasp_isa(C,ID1),
	#count { ID2:ooasp_assoc_gen(ASSOC,OPT,ID1,ID2) } = N,
	N < CMIN.
	%active(OBJECT).

ooasp_cv(lowerbound,ID1,M,(ASSOC,CMIN,N,C,OPT)):-
	lb_violation(lowerbound,ID1,M,(ASSOC,CMIN,N,C,OPT)),
	not lb_violation(lowerbound,ID1,_,(SUBASSOC,_,_,_,_)):ooasp_assoc_specialization(SUBASSOC,ASSOC).


%--- Associations are only allowed to something instantiated

ooasp_cv(no_instance_for_association,OBJECT,"Associated by {} to {} but not is not instantiated",(ASSOC,ID2)) :-
	ooasp_associated(ASSOC,OBJECT,ID2),
	not ooasp_isa(_,OBJECT).

ooasp_cv(no_instance_for_association,OBJECT,"Associated by {} to {} but not instantiated",(ASSOC,ID1)) :-
	ooasp_associated(ASSOC,ID1,OBJECT),
	not ooasp_isa(_,OBJECT).

ooasp_cv(no_instance_for_association,OBJECT,"Associated by {} to {} which is not instantiated",(ASSOC,ID2)) :-
	ooasp_associated(ASSOC,OBJECT,ID2),
	not ooasp_isa(_,ID2).

ooasp_cv(no_instance_for_association,OBJECT,"Associated by {} to {} which is not instantiated",(ASSOC,ID1)) :-
	ooasp_associated(ASSOC,ID1,OBJECT),
	not ooasp_isa(_,ID1).


%--- (USER INPUT) Type of association

ooasp_cv(wrongtypeinassoc,ID,"Associated by {} but is not of class {}",(ASSOC,C1)) :-
	%active(OBJECT),
	ooasp_associated(ASSOC,ID,_),
	ooasp_assoc(ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),
	not ooasp_isa(C1,ID).

ooasp_cv(wrongtypeinassoc,ID,"Associated by {} but is not of class {}",(ASSOC,C2)) :-
	%active(OBJECT),
	ooasp_associated(ASSOC,_,ID),
	ooasp_assoc(ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),
	not ooasp_isa(C2,ID).


%=======================================
% Values
%=======================================


%--- Missing attribute value
ooasp_cv(no_value,OBJECT,"Missing value for {}",(A,)) :-
	 ooasp_attr(C,A,enumint),
	 ooasp_attr_enum(C,A,_),
	 ooasp_isa(C,OBJECT),
	 not ooasp_attr_value(A,OBJECT,_).


%=======================================
% Special Constraint violations
%=======================================


%--- Unique attributes (Enumeration)

% The class C of the main object is in position 1

% The new object is of that class C
ooasp_cv(unique_attr, (OBJECT;ID1), "Attribute {} must be unique among all {}s associated by {} to {}",(ATTR,C,ASSOC,ID2,OBJECT )):-
	ooasp_special_cv(unique,(ASSOC, C, ATTR)),
	ooasp_assoc(ASSOC,C,_,_,_,_,_),
	ooasp_associated(ASSOC,OBJECT,ID2),
	ooasp_associated(ASSOC,ID1,ID2),
	OBJECT>ID1,
	ooasp_attr_value(ATTR,OBJECT,V),
	ooasp_attr_value(ATTR,ID1,V).

% The new object is of the other class
ooasp_cv(unique_attr, (ID3;ID1), "Attribute {} must be unique among all {}s associated by {} to {}",(ATTR,C,ASSOC,OBJECT)):-
	ooasp_special_cv(unique,(ASSOC, C, ATTR)),
	ooasp_assoc(ASSOC,C,_,_,_,_,_),
	ooasp_associated(ASSOC,ID3,OBJECT),
	ooasp_associated(ASSOC,ID1,OBJECT),
	ID3>ID1,
	ooasp_attr_value(ATTR,ID3,V),
	ooasp_attr_value(ATTR,ID1,V).

% The class C of the main object is in position 2

ooasp_cv(unique_attr, (OBJECT;ID1), "Attribute {} must be unique among all {}s associated by {} to {}",(ATTR,C,ASSOC,ID2,OBJECT )):-
	ooasp_special_cv(unique,(ASSOC, C, ATTR)),
	ooasp_assoc(ASSOC,_,_,_,C,_,_),
	ooasp_associated(ASSOC,ID2,OBJECT),
	ooasp_associated(ASSOC,ID2,ID1),
	OBJECT>ID1,
	ooasp_attr_value(ATTR,OBJECT,V),
	ooasp_attr_value(ATTR,ID1,V).

ooasp_cv(unique_attr, (ID3;ID1), "Attribute {} must be unique among all {}s associated by {} to {}",(ATTR,C,ASSOC,OBJECT )):-
	ooasp_special_cv(unique,(ASSOC, C, ATTR)),
	ooasp_assoc(ASSOC,_,_,_,C,_,_),
	ooasp_associated(ASSOC,OBJECT,ID3),
	ooasp_associated(ASSOC,OBJECT,ID1),
	ID3>ID1,
	ooasp_attr_value(ATTR,ID3,V),
	ooasp_attr_value(ATTR,ID1,V).



