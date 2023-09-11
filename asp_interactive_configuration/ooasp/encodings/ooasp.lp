% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

% ------------ Base programs
#const config_name = default_config_name.
#const kb_name = default_kb_name.
ooasp_configuration(kb_name,config_name).
#include "ooasp_aux_kb.lp". % Auxiliary predicates for the KB
#external guess. % The guessing part is active
#external check_potential_cv. % Checks for potential constraints apply
#external check_permanent_cv. % Checks for permanent constraints apply


% ------------ Incremental programs
#include "ooasp_user_input.lp". % User input with externals
#include "ooasp_aux_config.lp". % Auxiliay predicates fot the config
#include "ooasp_guess.lp". % Guess section
#include "ooasp_check.lp". % Check section

#include "ooasp_symmetry.lp". % Symmetry breaking constraints