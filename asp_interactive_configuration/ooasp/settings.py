
from importlib import resources

import ooasp.encodings

global encodings_path
encodings_path = resources.files(ooasp.encodings)
global racks_example_kb
racks_example_kb = "./examples/racks/kb.lp"
global racks_example_constraints
racks_example_constraints = "./examples/racks/constraints.lp"