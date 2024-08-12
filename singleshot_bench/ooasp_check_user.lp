
% ==============================================================================
% User input Values (General), when guessing values this should not be needed
% ==============================================================================

% %--- (USER INPUT) Attribute value must belong to instance class
ooasp_cv(no_instance_for_attribute,OBJECT,"Attribute {} not of selected class",(A,)) :-
	ooasp_attr(C1,A,T),
	user(ooasp_attr_value(A,OBJECT,V)),
	not ooasp_isa(C1,OBJECT).

%--- (USER INPUT) Attribute value must belong to instance
ooasp_cv(no_instance_for_attribute,OBJECT,"Value for {} assigned but instanciated",(A,)) :-
	user(ooasp_attr_value(A,OBJECT,V)),
	not ooasp_isa(_,OBJECT).

%--- (USER INPUT) Atribute value not from domain
ooasp_cv(value_not_domain,OBJECT,"Value {} for {} not from domain",(V,A)) :-
	 ooasp_attr(C,A,enumint),
	 ooasp_attr_enum(C,A,_),
	 ooasp_isa(C,OBJECT),
	 user(ooasp_attr_value(A,OBJECT,V)),
	 not ooasp_attr_enum(C,A,V).

%--- (USER INPUT) Multiple values for a value
ooasp_cv(conflicting_values,OBJECT,"Multiple values for {}: {},{}",(A,V1,V2)) :-
	 ooasp_attr(C,A,T),
	 user(ooasp_attr_value(A,OBJECT,V1)),
	 user(ooasp_attr_value(A,OBJECT,V2)),
	 V1<V2.

%--- (USER INPUT) Value outside range
ooasp_cv(value_outside_of_range,OBJECT,"Value for {} outside range {}<{}",(A,V,MIN)) :-
	 ooasp_attr(C,A,T),
	 ooasp_isa(C,OBJECT),
	 user(ooasp_attr_value(A,OBJECT,V)),
	 ooasp_attr_minInclusive(C,A,MIN),
	 V<MIN.

ooasp_cv(value_outside_of_range,OBJECT,"Value for {} outside range {}>{}",(A,V,MAX)) :-
	 ooasp_attr(C,A,T),
	 ooasp_isa(C,OBJECT),
	 user(ooasp_attr_value(A,OBJECT,V)),
	 ooasp_attr_maxInclusive(C,A,MAX),
	 V>MAX.