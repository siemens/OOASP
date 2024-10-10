% Copyright (c) 2024 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

% ooasp_cv(NAME,OBJECT,STR,ARGS)

#program domain(new_object, cls).

%=======================================
% Values
%=======================================
%--- Missing attribute value (Integer)
ooasp_cv(no_value,new_object,"Missing value for {}",(A,)) :-
	ooasp_attr(C,A,int),
	ooasp_isa(C,new_object),
	not &fsum{ooasp_attr_fvalue(A,new_object)}=ooasp_attr_fvalue(A,new_object).


%--- Unique attributes (Integer values (fclingo))

% The class C of the main object is in position 1

% The new object is of that class C
ooasp_cv(unique_attr, (new_object;ID1), "Attribute {} must be unique among all {}s associated by {} to {}",(ATTR,C,ASSOC,ID2,new_object )):-
	ooasp_attr(C,ATTR,int),
	ooasp_special_cv(unique,(ASSOC, C, ATTR)),
	ooasp_assoc(ASSOC,C,_,_,_,_,_),
	ooasp_associated(ASSOC,new_object,ID2),
	ooasp_associated(ASSOC,ID1,ID2),
	new_object>ID1,
	&fsum{ooasp_attr_fvalue(ATTR,new_object)}=ooasp_attr_fvalue(ATTR,ID1).

% The new object is of the other class
ooasp_cv(unique_attr, (ID3;ID1), "Attribute {} must be unique among all {}s associated by {} to {}",(ATTR,C,ASSOC,new_object)):-
	ooasp_attr(C,ATTR,int),
	ooasp_special_cv(unique,(ASSOC, C, ATTR)),
	ooasp_assoc(ASSOC,C,_,_,_,_,_),
	ooasp_associated(ASSOC,ID3,new_object),
	ooasp_associated(ASSOC,ID1,new_object),
	ID3>ID1,
	&fsum{ooasp_attr_fvalue(ATTR,ID3)}=ooasp_attr_fvalue(ATTR,ID1).

% The class C of the main object is in position 2

ooasp_cv(unique_attr, (new_object;ID1), "Attribute {} must be unique among all {}s associated by {} to {}",(ATTR,C,ASSOC,ID2,new_object )):-
	ooasp_attr(C,ATTR,int),
	ooasp_special_cv(unique,(ASSOC, C, ATTR)),
	ooasp_assoc(ASSOC,_,_,_,C,_,_),
	ooasp_associated(ASSOC,ID2,new_object),
	ooasp_associated(ASSOC,ID2,ID1),
	new_object>ID1,
	&fsum{ooasp_attr_fvalue(ATTR,new_object)}=ooasp_attr_fvalue(ATTR,ID1).

ooasp_cv(unique_attr, (ID3;ID1), "Attribute {} must be unique among all {}s associated by {} to {}",(ATTR,C,ASSOC,new_object )):-
	ooasp_attr(C,ATTR,int),
	ooasp_special_cv(unique,(ASSOC, C, ATTR)),
	ooasp_assoc(ASSOC,_,_,_,C,_,_),
	ooasp_associated(ASSOC,new_object,ID3),
	ooasp_associated(ASSOC,new_object,ID1),
	ID3>ID1,
	&fsum{ooasp_attr_fvalue(ATTR,ID3)}=ooasp_attr_fvalue(ATTR,ID1).



%--- (USER INPUT) Value outside range (Integers)

ooasp_cv(value_outside_of_range,new_object,"Value for {} outside min range {}",(A,MIN)) :-
	 ooasp_attr(C,A,int),
	 ooasp_isa(C,new_object),
	 &fsum{ooasp_attr_fvalue(A,new_object)}<MIN,
	 ooasp_attr_minInclusive(C,A,MIN).

ooasp_cv(value_outside_of_range,new_object,"Value for {} outside max range {}",(A,MAX)) :-
	 ooasp_attr(C,A,int),
	 ooasp_isa(C,new_object),
	 &fsum{ooasp_attr_fvalue(A,new_object)}>MAX,
	 ooasp_attr_maxInclusive(C,A,MAX).


%=======================================
% Special Constraint violations
%=======================================


%--- Unique attributes (Enumeration)

% The class C of the main object is in position 1

% The new object is of that class C
ooasp_cv(unique_attr, (new_object;ID1), "Attribute {} must be unique among all {}s associated by {} to {}",(ATTR,C,ASSOC,ID2,new_object )):-
	ooasp_special_cv(unique,(ASSOC, C, ATTR)),
	ooasp_assoc(ASSOC,C,_,_,_,_,_),
	ooasp_associated(ASSOC,new_object,ID2),
	ooasp_associated(ASSOC,ID1,ID2),
	new_object>ID1,
	ooasp_attr_value(ATTR,new_object,V),
	ooasp_attr_value(ATTR,ID1,V).

% The new object is of the other class
ooasp_cv(unique_attr, (ID3;ID1), "Attribute {} must be unique among all {}s associated by {} to {}",(ATTR,C,ASSOC,new_object)):-
	ooasp_special_cv(unique,(ASSOC, C, ATTR)),
	ooasp_assoc(ASSOC,C,_,_,_,_,_),
	ooasp_associated(ASSOC,ID3,new_object),
	ooasp_associated(ASSOC,ID1,new_object),
	ID3>ID1,
	ooasp_attr_value(ATTR,ID3,V),
	ooasp_attr_value(ATTR,ID1,V).

% The class C of the main object is in position 2

ooasp_cv(unique_attr, (new_object;ID1), "Attribute {} must be unique among all {}s associated by {} to {}",(ATTR,C,ASSOC,ID2,new_object )):-
	ooasp_special_cv(unique,(ASSOC, C, ATTR)),
	ooasp_assoc(ASSOC,_,_,_,C,_,_),
	ooasp_associated(ASSOC,ID2,new_object),
	ooasp_associated(ASSOC,ID2,ID1),
	new_object>ID1,
	ooasp_attr_value(ATTR,new_object,V),
	ooasp_attr_value(ATTR,ID1,V).

ooasp_cv(unique_attr, (ID3;ID1), "Attribute {} must be unique among all {}s associated by {} to {}",(ATTR,C,ASSOC,new_object )):-
	ooasp_special_cv(unique,(ASSOC, C, ATTR)),
	ooasp_assoc(ASSOC,_,_,_,C,_,_),
	ooasp_associated(ASSOC,new_object,ID3),
	ooasp_associated(ASSOC,new_object,ID1),
	ID3>ID1,
	ooasp_attr_value(ATTR,ID3,V),
	ooasp_attr_value(ATTR,ID1,V).

%--- Unique attributes (Integer values (fclingo))

% The class C of the main object is in position 1

% The new object is of that class C
ooasp_cv(unique_attr, (new_object;ID1), "Attribute {} must be unique among all {}s associated by {} to {}",(ATTR,C,ASSOC,ID2,new_object )):-
	ooasp_attr(C,ATTR,int),
	ooasp_special_cv(unique,(ASSOC, C, ATTR)),
	ooasp_assoc(ASSOC,C,_,_,_,_,_),
	ooasp_associated(ASSOC,new_object,ID2),
	ooasp_associated(ASSOC,ID1,ID2),
	new_object>ID1,
	&fsum{ooasp_attr_fvalue(ATTR,new_object)}=ooasp_attr_fvalue(ATTR,ID1).

% The new object is of the other class
ooasp_cv(unique_attr, (ID3;ID1), "Attribute {} must be unique among all {}s associated by {} to {}",(ATTR,C,ASSOC,new_object)):-
	ooasp_attr(C,ATTR,int),
	ooasp_special_cv(unique,(ASSOC, C, ATTR)),
	ooasp_assoc(ASSOC,C,_,_,_,_,_),
	ooasp_associated(ASSOC,ID3,new_object),
	ooasp_associated(ASSOC,ID1,new_object),
	ID3>ID1,
	&fsum{ooasp_attr_fvalue(ATTR,ID3)}=ooasp_attr_fvalue(ATTR,ID1).

% The class C of the main object is in position 2

ooasp_cv(unique_attr, (new_object;ID1), "Attribute {} must be unique among all {}s associated by {} to {}",(ATTR,C,ASSOC,ID2,new_object )):-
	ooasp_attr(C,ATTR,int),
	ooasp_special_cv(unique,(ASSOC, C, ATTR)),
	ooasp_assoc(ASSOC,_,_,_,C,_,_),
	ooasp_associated(ASSOC,ID2,new_object),
	ooasp_associated(ASSOC,ID2,ID1),
	new_object>ID1,
	&fsum{ooasp_attr_fvalue(ATTR,new_object)}=ooasp_attr_fvalue(ATTR,ID1).

ooasp_cv(unique_attr, (ID3;ID1), "Attribute {} must be unique among all {}s associated by {} to {}",(ATTR,C,ASSOC,new_object )):-
	ooasp_attr(C,ATTR,int),
	ooasp_special_cv(unique,(ASSOC, C, ATTR)),
	ooasp_assoc(ASSOC,_,_,_,C,_,_),
	ooasp_associated(ASSOC,new_object,ID3),
	ooasp_associated(ASSOC,new_object,ID1),
	ID3>ID1,
	&fsum{ooasp_attr_fvalue(ATTR,ID3)}=ooasp_attr_fvalue(ATTR,ID1).

