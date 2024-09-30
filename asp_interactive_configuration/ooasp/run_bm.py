from ooasp.interactive import InteractiveConfigurator
from ooasp.kb import OOASPKnowledgeBase
import ooasp.utils as utils
from ooasp import settings
from argparse import ArgumentParser
from ooasp.config import *
from benchmarks import *

def get_parser() -> ArgumentParser:
    """
    Return the parser for command line options.
    """
    parser = ArgumentParser(
        prog="ooasp",
    )
    parser.add_argument("--element", type=int, default=0)
    parser.add_argument("--rack", type=int, default=0)
    parser.add_argument("--module", type=int, default=0)
    parser.add_argument("--frame", type=int, default=0)
    # ------------------------Specific-----------------------
    parser.add_argument("--rackSingle", type=int, default=0)
    parser.add_argument("--rackDouble", type=int, default=0)
    parser.add_argument("--elementA", type=int, default=0)
    parser.add_argument("--elementB", type=int, default=0)
    parser.add_argument("--elementC", type=int, default=0)
    parser.add_argument("--elementD", type=int, default=0)
    parser.add_argument("--moduleI", type=int, default=0)
    parser.add_argument("--moduleII", type=int, default=0)
    parser.add_argument("--moduleIII", type=int, default=0)
    parser.add_argument("--moduleIV", type=int, default=0)
    parser.add_argument("--moduleV", type=int, default=0)
    return parser

def setup_config(initial_objects):
    conf = InteractiveConfigurator(kb=OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb), config_name="configuration")
    for o in initial_objects:
        conf.new_object(o)
    print(f"-----Solving for objects: {initial_objects}")
    found = conf.extend_incrementally()
    return conf  

if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()

    initial_objects = []

    initial_objects += ["frame"] * args.frame

    initial_objects += ["rackDouble"] * args.rackDouble
    initial_objects += ["rackSingle"] * args.rackSingle
    initial_objects += ["rack"] * args.rack

    initial_objects += ["elementA"] * args.elementA
    initial_objects += ["elementB"] * args.elementB
    initial_objects += ["elementC"] * args.elementC
    initial_objects += ["elementD"] * args.elementD
    initial_objects += ["element"] * args.element

    initial_objects += ["module"] * args.module
    initial_objects += ["moduleI"] * args.moduleI
    initial_objects += ["moduleII"] * args.moduleII
    initial_objects += ["moduleIII"] * args.moduleIII
    initial_objects += ["moduleIV"] * args.moduleIV
    initial_objects += ["moduleV"] * args.moduleV

    config = setup_config(initial_objects)
    print("-----Found configuration:")
    print(config.found_config)
    print("----------DONE----------")

    