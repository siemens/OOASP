# Copyright (c) 2024 Siemens AG Oesterreich
# SPDX-License-Identifier: MIT

from importlib import resources

import ooasp.encodings

global encodings_path
encodings_path = resources.files(ooasp.encodings)
global racks_example_kb
racks_example_kb = "./examples/racks/kb.lp"
global racks_example_attr_constraints
racks_example_attr_constraints = "./examples/racks/attribute_constraints.lp"
global racks_example_obj_constraints
racks_example_attr_obj_constraints = "./examples/racks/object_constraints.lp"
global metro_example_kb
metro_example_kb = "./examples/metro/kb.lp"
global metro_example_constraints
metro_example_constraints = "./examples/metro/constraints.lp"
global metrof_example_kb
metrof_example_kb = "./examples/metro/fkb.lp"
global metrof_example_constraints
metrof_example_constraints = "./examples/metro/fconstraints.lp"
global metro_small_example_kb
metro_small_example_kb = "./examples/metro_small/kb.lp"
global metro_small_example_constraints
metro_small_example_constraints = "./examples/metro_small/constraints.lp"
global metrof_small_example_kb
metrof_small_example_kb = "./examples/metro_small/fkb.lp"
global metrof_small_example_constraints
metrof_small_example_constraints = "./examples/metro_small/fconstraints.lp"
