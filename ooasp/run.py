import json
import os

import time
from argparse import ArgumentParser

from clingo import Control, Number, Function

from importlib import resources

import ooasp.settings as settings


from clingraph.orm import Factbase
from clingraph.graphviz import compute_graphs, render
from clingraph.clingo_utils import ClingraphContext


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
    print(f"Grouding {size} {o}")
    ctl.ground([("domain", [Number(size), Function(o, [])])])
    if size > 0:
        ctl.release_external(Function("active", [Number(size - 1)]))
    ctl.assign_external(Function("active", [Number(size)]), True)


def add_object(ctl, o, size, association=None):
    print(f"\tAdding object  {o},{size}")
    ctl.add("domain", [str(size), "object"], f"user(ooasp_isa({o},{size})).")
    if association and add_associations:
        assoc_atom = (
            f"ooasp_associated({association[0]},{association[1]},{association[2]})"
        )
        print("\tAdding association:", assoc_atom)
        ctl.add("domain", [str(size), "object"], f"user({assoc_atom}).")

        ctl.add(
            "domain",
            [str(size), "object"],
            f"{assoc_atom}.",
        )

    ground(ctl, size, o)


def _get_cautious(ctl, project=False):
    ctl.assign_external(Function("check_potential_cv"), False)
    ctl.configuration.solve.models = "0"
    ctl.configuration.solve.enum_mode = "cautious"
    ctl.configuration.solve.opt_mode = "optN"
    if project:
        ctl.configuration.solve.project = "project"
    with ctl.solve(yield_=True) as hdn:
        cautious_model = None
        for model in hdn:
            cautious_model = model.symbols(shown=True)
        if cautious_model is None:
            print("\tUNSAT cautious!")
            # print(model)
    ctl.assign_external(Function("check_potential_cv"), True)
    ctl.configuration.solve.opt_mode = "ignore"
    ctl.configuration.solve.models = "1"
    ctl.configuration.solve.enum_mode = "auto"
    ctl.configuration.solve.project = "auto"
    return cautious_model


def create_from_cautious(ctl, size, project=False):
    print("---> Create from cautious")
    cautious = _get_cautious(ctl)
    added = 0
    if cautious is None:
        print(f"<-- Cautious opt added {added} objects")
        return 0
    print("\tAll cautious optimal projected:", "\n\t".join([str(s) for s in cautious]))
    for s in cautious:
        if s.match("ooasp_cv", 4):
            if str(s.arguments[0]) != "lowerbound":
                continue
            print("\t** Focusing on: ", s)
            assoc, cmin, n, c, opt, _ = s.arguments[3].arguments
            for _ in range(n.number, cmin.number):
                if str(opt) == "1":
                    a = (str(assoc), str(s.arguments[1]), size)
                else:
                    a = (str(assoc), size, str(s.arguments[1]))
                add_object(ctl, c.name, size, a)
                size += 1
                added += 1
        if added > 0:
            break
    print(f"<--- Cautious opt added {added} objects")
    return added


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

    # ctl.add("base", [], self.fb.asp_str())
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
    parser.add_argument("--racksS", type=int, default=0)
    parser.add_argument("--racksD", type=int, default=0)
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

    # use_cautious_generate = True
    use_cautious_generate = args.cautious
    add_associations = args.cautious_assoc

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
    # ctl.load("examples/racks/constraints.lp")
    ctl.load("ooasp/encodings/ooasp_simple.lp")
    if use_cautious_generate:
        ctl.load("ooasp/encodings/ooasp_cautious_opt.lp")

    ctl.ground([("base", [])])
    ctl.configuration.solve.opt_mode = "ignore"

    next_id = 1
    initial_objects = []

    initial_objects += ["frame"] * args.frame

    initial_objects += ["rackDouble"] * args.racksD
    initial_objects += ["rackSingle"] * args.racksS
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
    while not done:
        print(f"\nSolving for size {next_id-1}...")
        res = ctl.solve(on_model=on_model)
        if res.satisfiable:
            print("     Found model")
            done = True
            break
        print(f"    No configuration found for size {next_id-1}")
        start_size = next_id
        stats[next_id - 1] = ctl.statistics["summary"]["times"]
        try_new = True
        if use_cautious_generate:
            added = create_from_cautious(ctl, next_id, project=args.project)
            next_id += added
            try_new = added == 0
        while try_new:
            ground(ctl, next_id, "object")
            next_id += 1
            if next_id >= start_size + step_size:
                try_new = False

    end = time.time()
    stats[next_id - 1] = ctl.statistics["summary"]["times"]

    print("Done!")
    os.makedirs('benchmarks/latest', exist_ok=True)
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
