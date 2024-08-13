
% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

% ------------ Base programs
#const config_name = default_config_name.
#const kb_name = default_kb_name.
ooasp_configuration(kb_name,config_name).
#include "ooasp_aux_kb.lp". % Auxiliary predicates for the KB
guess. % The guessing part is active
#external check_potential_cv.[true] % Checks for potential constraints apply
check_permanent_cv. % Checks for permanent constraints apply


% ------------ Incremental programs
#include "ooasp_aux_config.lp". % Auxiliay predicates fot the config
#include "ooasp_guess.lp". % Guess section
#include "ooasp_check.lp". % Check section

#include "ooasp_symmetry.lp". % Symmetry breaking constraints
#include "ooasp_upper_bound.lp". % Calculates global needs

#show lb_at_least/6.
#show upper_filled/5.
#show lower_global/5.
#show association_needed_lb/4.
#show .

#program domain(new_object, cls).

:- user(ooasp_isa(C,new_object  )),
not ooasp_isa(C,new_object).