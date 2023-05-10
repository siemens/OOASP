% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

% ------------ Base programs
#const config_name = racks_config_1.
#const kb_name = v1.
ooasp_configuration(kb_name,config_name).
#include "ooasp_aux_kb.lp". % Auxiliary predicates for the KB
#external guess. % The guessing part is active
#external check_potential_cv. % Checks for potential constraints apply
#external check_permanent_cv. % Checks for full constraints apply


% ------------ Incremental programs
#include "ooasp_user_input.lp". % User input with externals
#include "ooasp_aux_config.lp". % Auxiliay predicates fot the config
#include "ooasp_guess.lp". % Guess section
#include "ooasp_check.lp". % Check section

use_symmetry.
#include "ooasp_symmetry.lp". % Symmetry breaking constraints
