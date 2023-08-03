% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

#program base.

% transitive closure
ooasp_subclass(SUB,SUPER2) :-
    ooasp_subclass(SUB,SUPER1),
    ooasp_subclass(SUPER1,SUPER2).

ooasp_subclass_ref(C1,C2):-ooasp_subclass(C1,C2).
ooasp_subclass_ref(C,C):-ooasp_class(C).


% derive domain for boolean attributes
ooasp_attr_enum(C,N,"true") :-
    ooasp_attr(C,N,"boolean").
ooasp_attr_enum(C,N,"false") :-
    ooasp_attr(C,N,"boolean").

% true, if attribute has domain
ooasp_attr_hasdomain(C,N) :-
    ooasp_attr_enum(C,N,D).

ooasp_attr_enum(C,N,MIN..MAX):-
    ooasp_attr(C,N,int),
    ooasp_attr_minInclusive(C,N,MIN),
    ooasp_attr_maxInclusive(C,N,MAX).

% leafclasses are classes without subclasses
ooasp_leafclass(C) :-
     ooasp_class(C),
     not ooasp_subclass(_,C).

% Defines the limits for an association based on the class number

% ooasp_assoc_limit(ASSOC,min,1,C1,C2MIN)
% The association ASSOC must be from a C1 element to at least C2MIN elements

ooasp_assoc_limit(ASSOC,min,1,C1,C2MIN):-
	ooasp_assoc(ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX).

ooasp_assoc_limit(ASSOC,max,1,C1,C2MAX):-
	ooasp_assoc(ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX).

ooasp_assoc_limit(ASSOC,min,2,C2,C1MIN):-
	ooasp_assoc(ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX).

ooasp_assoc_limit(ASSOC,max,2,C2,C1MAX):-
	ooasp_assoc(ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX).
