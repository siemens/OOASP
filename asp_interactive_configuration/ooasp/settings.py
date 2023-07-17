
from importlib import resources

import ooasp.encodings.encodings_basic
import ooasp.encodings.encodings_paper

def init(opt):
    global encodings_path
    global racks_example_kb
    global racks_example_constraints
    global include_config
    global include_kb
    if opt == 'paper':
        encodings_path = resources.files(ooasp.encodings.encodings_paper)
        racks_example_kb = "./examples/paper/racks/kb.lp"
        racks_example_constraints = "./examples/paper/racks/constraints.lp"
    else:
        encodings_path = resources.files(ooasp.encodings.encodings_basic)
        racks_example_kb = "./examples/basic/racks/kb.lp"
        racks_example_constraints = "./examples/basic/racks/constraints.lp"


    include_config = opt not in ['paper']
    include_kb = opt not in ['paper']