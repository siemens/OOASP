import json

import time
from argparse import ArgumentParser

from clingo import Control, Number, Function
from clingo import parse_term
import ooasp.settings as settings


from clingraph.orm import Factbase
from clingraph.graphviz import compute_graphs, render
from clingraph.clingo_utils import ClingraphContext

config = []


def log(*args):
    print(*args)
    pass


def generate_output_path(args):
    non_zero = [
        opt
        for opt in args.__dict__
        if type(args.__dict__[opt]) is int and args.__dict__[opt] != 0
    ]
    fstr = ""
    for opt in non_zero:
        fstr += "-" + opt[0]
        fstr += "".join([letter for letter in opt if letter.isupper()])
        fstr += str(args.__dict__[opt])
    return fstr[1:]


def ground(ctl, size, o):
    log(f"\t\tGrounding {size} {o}")
    ctl.ground([("domain", [Number(size), Function(o, [])])])
    if size > 0:
        ctl.release_external(Function("active", [Number(size - 1)]))
    ctl.assign_external(Function("active", [Number(size)]), True)


def get_assoc_atom(association):
    assoc_atom = f"ooasp_associated({association[0]},{association[1]},{association[2]})"
    return assoc_atom


def add_object(ctl, o, size, association=None):
    log(f"\t\tAdding object  {o},{size}")
    obj_atom = f"ooasp_isa({o},{size})"
    ctl.add("domain", [str(size), "object"], f"user({obj_atom}).")
    config.append(obj_atom)
    config.append(f"user({obj_atom})")
    assoc = []
    if association is not None:
        assoc = [get_assoc_atom(association)]

    ground(ctl, size, o)
    return assoc


def _get_brave(ctl, assumptions):
    ctl.assign_external(Function("check_potential_cv"), False)
    ctl.assign_external(Function("computing_brave"), True)
    ctl.configuration.solve.models = "0"
    ctl.configuration.solve.enum_mode = "brave"
    with ctl.solve(yield_=True, assumptions=assumptions) as hdn:
        brave_model = None
        for model in hdn:
            brave_model = model.symbols(shown=True)
        if brave_model is None:
            log("\tUNSAT brave!")
    ctl.assign_external(Function("check_potential_cv"), True)
    ctl.assign_external(Function("computing_brave"), False)
    ctl.configuration.solve.models = "1"
    ctl.configuration.solve.enum_mode = "auto"
    ctl.configuration.solve.project = "auto"
    return brave_model


def _get_cautious(ctl, assumptions):
    ctl.assign_external(Function("check_potential_cv"), False)
    ctl.assign_external(Function("computing_cautious"), True)
    ctl.configuration.solve.models = "0"
    ctl.configuration.solve.enum_mode = "cautious"
    with ctl.solve(yield_=True, assumptions=assumptions) as hdn:
        cautious_model = None
        for model in hdn:
            cautious_model = model.symbols(shown=True)
        if cautious_model is None:
            log("\tUNSAT cautious!")
    ctl.assign_external(Function("check_potential_cv"), True)
    ctl.assign_external(Function("computing_cautious"), False)
    ctl.configuration.solve.models = "1"
    ctl.configuration.solve.enum_mode = "auto"
    ctl.configuration.solve.project = "auto"
    return cautious_model


def print_all(ctl):
    ctl.assign_external(Function("check_potential_cv"), False)
    ctl.configuration.solve.models = "0"
    ctl.configuration.solve.enum_mode = "auto"
    with ctl.solve(yield_=True) as hdn:
        for model in hdn:
            log(model.symbols(shown=True))


def create_assoc_from_brave(ctl, size, assumptions):
    log("\n---> Smart brave expand")
    brave = _get_brave(ctl, assumptions)
    added = 0
    # log(
    #     "\tAll brave:\n\t",
    #     "\n\t".join(["____ " + str(s) for s in brave]),
    # )
    if brave is None:
        log(f"<-- brave added {added} assoc")
        return []
    log("\tWill check for: association_needed_lb")
    for s in brave:
        if s.match("association_needed_lb", 4):
            log("\t********** Apply ", s)
            assoc, id1, id2, _ = s.arguments
            a = (str(assoc), id1, id2)
            assoc_atom = get_assoc_atom(a)
            log(f"<--- Smart brave expand added {assoc_atom}")
            return [assoc_atom]
    return []


def create_from_cautious(ctl, size, assumptions):
    log("\n---> Smart expand")
    cautious = _get_cautious(ctl, assumptions)
    added = 0
    if cautious is None:
        log(f"<-- Cautious added {added} objects")
        return 0, []
    log(
        "\tAll cautious optimal projected:\n\t",
        "\n\t".join(["____ " + str(s) for s in cautious]),
    )
    added_key = None
    added_assoc = []
    log("\tWill check for: lb_at_least")
    for s in cautious:
        if s.match("lb_at_least", 6):
            o_id, assoc, needed, c, opt, _ = s.arguments
            if added_key is None:
                log("\t********** Apply ", s)
                added_key = (o_id, assoc)
            if added_key != (o_id, assoc):
                continue
            for _ in range(added, needed.number):
                if str(opt) == "1":
                    a = (str(assoc), o_id, size)
                else:
                    a = (str(assoc), size, o_id)
                added_assoc += add_object(ctl, c.name, size, a)
                size += 1
                added += 1
    if added == 0:
        log("\tWill check for: upper_filled")
        for s in cautious:
            if added > 0:
                break
            if s.match("upper_filled", 5):
                log("\t********** Apply ", s)
                _, _, c2, needed, _ = s.arguments
                for _ in range(added, needed.number):
                    added_assoc += add_object(ctl, c2.name, size)
                    size += 1
                    added += 1
                break

    if added == 0:
        log("\tWill check for: lower_global")
        for s in cautious:
            if added > 0:
                break
            if s.match("lower_global", 5):
                log("\t********** Apply ", s)
                c1, _, _, needed, _ = s.arguments
                for _ in range(added, needed.number):
                    added_assoc += add_object(ctl, c1.name, size)
                    size += 1
                    added += 1
                break

    log(f"<--- Smart expand added {added} objects")
    return added, added_assoc


def save_png(config, directory: str = "./out"):
    """
    Saves the configuration as a png using clingraph
    """
    ctl = Control(["--warn=none"])
    fbs = []
    path = settings.encodings_path.joinpath("viz_config.lp")
    ctl.load(str(path))
    path = settings.encodings_path.joinpath("ooasp_aux_kb.lp")
    ctl.load(str(path))
    ctl.load("examples/racks/kb.lp")

    ctl.add("base", [], config)
    ctl.ground([("base", [])], ClingraphContext())
    ctl.solve(
        on_model=lambda m: fbs.append(Factbase.from_model(m, default_graph="config"))
    )
    graphs = compute_graphs(fbs[0])
    render(graphs, format="png", name_format="config", directory=directory, view=True)


"""
The command line parser for the project.
"""


def get_parser() -> ArgumentParser:
    """
    Return the parser for command line options.
    """
    parser = ArgumentParser(
        prog="ooasp",
    )
    parser.add_argument("--cautious", action="store_true")
    parser.add_argument("--cautious-assoc", action="store_true")
    parser.add_argument("--project", action="store_true")
    parser.add_argument("--view", action="store_true")
    # ------------------------General------------------------
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


# ========================== Main

if __name__ == "__main__":

    parser = get_parser()
    args = parser.parse_args()

    start = time.time()
    ctl = Control(
        [
            "1",
            "--warn=none",
            f"-c config_name=c1",
            f"-c kb_name=k1",
            "-t3",
            "--project=show",
        ]
    )
    ctl.load("examples/racks/kb.lp")
    ctl.load("ooasp/encodings/ooasp_simple.lp")

    ctl.ground([("base", [])])

    next_id = 1
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

    for o in initial_objects:
        add_object(ctl, o, next_id)
        next_id += 1

    # ---- Find incrementally

    model = []

    def on_model(m):
        global model
        model = [str(s) + "." for s in m.symbols(atoms=True)]

    step_size = 1
    stats = {}
    done = False
    assoc = []

    while not done:
        assumptions = [(parse_term(a), True) for a in assoc]
        added, assoc_added = create_from_cautious(ctl, next_id, assumptions)
        next_id += added
        assoc += assoc_added
        if added > 0:
            continue
        brave_assoc_added = create_assoc_from_brave(ctl, next_id, assumptions)
        assoc += brave_assoc_added
        if len(brave_assoc_added) > 0:
            continue
        # Uncomment to save the configuration before the solving step as a png
        # save_png("\n".join([str(c)+"." for c in config]), directory="out/solve")
        log(f"\n==============================")
        log(f"Solving for size {next_id-1}...")
        # log(assumptions)
        ctl.configuration.solve.models = "1"
        res = ctl.solve(on_model=on_model, assumptions=assumptions)
        if res.satisfiable:
            log("     Found model")
            done = True
            continue
        log(f"No solution found")
        ground(ctl, next_id, "object")
        next_id += 1

    end = time.time()
    stats[next_id - 1] = ctl.statistics["summary"]["times"]

    log("Done!")
    out_name = f"benchmarks/latest/{generate_output_path(args)}"
    if args.cautious:
        out_name += "-c"
    if args.cautious_assoc:
        out_name += "-ca"
    if args.project:
        out_name += "-p"

    with open(f"{out_name}.txt", "w") as f:
        print(json.dumps(stats, indent=4), file=f)
        print("TOTAL TIME: ", sum([r["total"] for r in stats.values()]), file=f)
        print("TOTAL SOLVE TIME: ", sum([r["solve"] for r in stats.values()]), file=f)
        print("Actual TIME: ", end - start, file=f)

    if args.view:
        save_png("\n".join(model))

    print("RUNTIME: ", end - start)
