% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

#program base.

#const use_dl = false.

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
    ooasp_attr(C,N,enumint),
    ooasp_attr_minInclusive(C,N,MIN),
    ooasp_attr_maxInclusive(C,N,MAX).

ooasp_attr_fdom(C,N,MIN..MAX):-
    ooasp_attr(C,N,int),
    ooasp_attr_minInclusive(C,N,MIN),
    ooasp_attr_maxInclusive(C,N,MAX).

% leafclasses are classes without subclasses
ooasp_leafclass(C) :-
     ooasp_class(C),
     not ooasp_subclass(_,C).


% ooasp_assoc_limit(ASSOC,min,1,C1,C2MIN,C2)
% The association ASSOC must be from a C1 object to at least C2MIN objects of class C2

ooasp_assoc_limit(ASSOC,min,1,C1,C2MIN,C2):-
	ooasp_assoc(ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX).

ooasp_assoc_limit(ASSOC,max,1,C1,C2MAX,C2):-
	ooasp_assoc(ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX).

ooasp_assoc_limit(ASSOC,min,2,C2,C1MIN,C1):-
	ooasp_assoc(ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX).

ooasp_assoc_limit(ASSOC,max,2,C2,C1MAX,C1):-
	ooasp_assoc(ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX).
