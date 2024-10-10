% Copyright (c) 2024 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT


#program domain(new_object, cls).

% Numerical Attributes (fclingo)

&fin{MIN..MAX} =: ooasp_attr_fvalue(A,new_object):-
	ooasp_attr_int(new_object, A, MIN, MAX),
    guess.
