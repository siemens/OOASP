
from importlib import resources

import ooasp.encodings.encodings_basic
import ooasp.encodings.encodings_paper
import ooasp.encodings.encodings_defined

def init(opt):
    global option
    global encodings_path
    global racks_example_kb
    global racks_example_constraints
    global include_config
    global include_kb
    global ground_cls
    option=opt
    if opt == 'paper':
        encodings_path = resources.files(ooasp.encodings.encodings_paper)
        racks_example_kb = "./examples/paper/racks/kb.lp"
        racks_example_constraints = "./examples/paper/racks/constraints.lp"
    elif opt == 'defined':
        encodings_path = resources.files(ooasp.encodings.encodings_defined)
        racks_example_kb = "./examples/defined/racks/kb.lp"
        racks_example_constraints = "./examples/defined/racks/constraints.lp"
    elif opt=='basic':
        encodings_path = resources.files(ooasp.encodings.encodings_basic)
        racks_example_kb = "./examples/basic/racks/kb.lp"
        racks_example_constraints = "./examples/basic/racks/constraints.lp"
    else:
        raise RuntimeError(f"Invalid setting option {opt}")

    include_config = opt == 'basic'
    include_kb = opt == 'basic'
    ground_cls = opt == 'defined'