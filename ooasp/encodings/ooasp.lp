
% Copyright (c) 2024 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

% ------------ Base programs
#const config_name = default_config_name.
#const kb_name = default_kb_name.
ooasp_configuration(kb_name,config_name).
#include "ooasp_aux_kb.lp". % Auxiliary predicates for the KB
#include "ooasp_defined.lp". % Defined predicates
guess. % The guessing part is active
#external check_potential_cv.[true] % Checks for potential constraints apply
check_permanent_cv. % Checks for permanent constraints apply


% ------------ Incremental programs
#include "ooasp_aux_config.lp". % Auxiliay predicates fot the config
#include "ooasp_guess.lp". % Guess section
#include "ooasp_check.lp". % Check section

#include "ooasp_symmetry.lp". % Symmetry breaking constraints
#include "ooasp_smart_generation.lp". % Functions for smart generation

% !!!!!!!!!!!! Show statements. Notice that anything that is used in the smart generation functions
% as well as clinguin UI encoding should be shown to avoid incorrect results.

#show assoc_needs_object/6.
#show global_ub_gap/3.
#show global_lb_gap/3.
#show association_possible/4.
#show .

% Configuration information display
#show ooasp_isa/2.
#show ooasp_attr_value/3.
#show ooasp_associated/3.