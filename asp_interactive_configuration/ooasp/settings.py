
from importlib import resources

import ooasp.encodings

global encodings_path
encodings_path = resources.files(ooasp.encodings)
global racks_example_kb
racks_example_kb = "./examples/racks/kb.lp"
global racks_example_constraints
racks_example_constraints = "./examples/racks/constraints.lp"
global metro_example_kb
metro_example_kb = "./examples/metro/kb.lp"
global metro_example_constraints
metro_example_constraints = "./examples/metro/constraints.lp"
global metrof_example_kb
metrof_example_kb = "./examples/metro/fkb.lp"
global metrof_example_constraints
metrof_example_constraints = "./examples/metro/fconstraints.lp"