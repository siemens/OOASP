
% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

% ------------ Base programs
#const config_name = default_config_name.
#const kb_name = default_kb_name.
ooasp_configuration(kb_name,config_name).
#include "ooasp_aux_kb.lp". % Auxiliary predicates for the KB
guess. % The guessing part is active
% check_potential_cv. % Checks for potential constraints apply
% check_permanent_cv. % Checks for permanent constraints apply
#external check_potential_cv.[true] % Checks for potential constraints apply
check_permanent_cv. % Checks for permanent constraints apply


% ------------ Incremental programs
% #include "ooasp_user_input.lp". % User input with externals
#include "ooasp_aux_config.lp". % Auxiliay predicates fot the config
#include "ooasp_guess.lp". % Guess section
#include "ooasp_check.lp". % Check section

#include "ooasp_symmetry.lp". % Symmetry breaking constraints

#show ooasp_isa/2.
#show ooasp_cv/4.
#show user/1.
#show user2/1.

#program domain(new_object, cls).

:- user(ooasp_isa(C,new_object)),
not ooasp_isa(C,new_object).

