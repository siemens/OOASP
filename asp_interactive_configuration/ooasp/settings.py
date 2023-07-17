
from importlib import resources

import ooasp.encodings
import ooasp.encodings_paper

def init(opt):
    global encodings_path
    global include_config
    global include_kb
    if opt == 'paper':
        encodings_path = resources.files(ooasp.encodings_paper)
    else:
        encodings_path = resources.files(ooasp.encodings)

    include_config = opt not in ['paper']
    include_kb = opt not in ['paper']