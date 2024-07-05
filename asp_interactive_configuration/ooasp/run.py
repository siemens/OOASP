import json

import time
from argparse import ArgumentParser

from clingo import Control, Number, Function

def generate_output_path(args):
    non_zero = [opt for opt in args.__dict__ if type(args.__dict__[opt]) is int and args.__dict__[opt] != 0]
    fstr = ""
    for opt in non_zero:
        fstr += '-'+opt[0]
        fstr += ''.join([letter for letter in opt if letter.isupper()])
        fstr += str(args.__dict__[opt])
        print(opt)
    return fstr[1:]

def ground(ctl, size, o):
    print(f"Grouding {size} {o}")
    ctl.ground([("domain", [Number(size), Function(o, [])])])
    if size > 0:
        ctl.release_external(Function("active", [Number(size - 1)]))
    ctl.assign_external(Function("active", [Number(size)]), True)


def add_object(ctl, o, size, association=None):
    print(f"Adding object  {o},{size}")
    ctl.add("domain", [str(size), "object"], f"user(ooasp_isa({o},{size})).")
    if association and add_associations:
        print("Adding association ")
        print(f"ooasp_associated({association[0]},{association[1]},{association[2]})")
        ctl.add(
            "domain",
            [str(size), "object"],
            f"ooasp_associated({association[0]},{association[1]},{association[2]}).",
        )

    ground(ctl, size, o)


def on_model(m):
    print("Model")
    print(m)


def _get_cautious(ctl):
    ctl.assign_external(Function("check_potential_cv"), False)
    ctl.configuration.solve.models = "0"
    ctl.configuration.solve.enum_mode = "cautious"
    ctl.configuration.solve.opt_mode = "optN"
    with ctl.solve(yield_=True) as hdn:
        cautious_model = None
        for model in hdn:
            cautious_model = model.symbols(atoms=True)
    ctl.assign_external(Function("check_potential_cv"), True)
    ctl.configuration.solve.opt_mode = "ignore"
    ctl.configuration.solve.models = "1"
    ctl.configuration.solve.enum_mode = "auto"
    return cautious_model


def create_from_cautious(ctl, size):
    print("--- Create from cautious")
    cautious = _get_cautious(ctl)
    added = 0
    if cautious is None:
        print(f"--- Cautious opt added {added} objects")
        return 0
    for s in cautious:
        if s.match("ooasp_cv", 4):
            print(s)
            if str(s.arguments[0]) != "lowerbound":
                continue
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
    print(f"--- Cautious opt added {added} objects")
    return added


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
    #------------------------General------------------------
    parser.add_argument("--element", type=int, default=0)
    parser.add_argument("--rack", type=int, default=0)
    parser.add_argument("--module", type=int, default=0)
    parser.add_argument("--frame", type=int, default=0)
    #------------------------Specific-----------------------
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
    ctl = Control(["1", "--warn=none", f"-c config_name=c1", f"-c kb_name=k1", "-t3"])
    ctl.load("examples/racks/kb.lp")
    ctl.load("examples/racks/constraints.lp")
    ctl.load("ooasp/encodings/ooasp_simple.lp")
    if use_cautious_generate:
        ctl.load("ooasp/encodings/ooasp_cautious_opt.lp")

    ctl.ground([("base", [])])
    ctl.configuration.solve.opt_mode = "ignore"

    size = 1
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
        add_object(ctl, o, size)
        size += 1

    # ---- Find incrementally

    print(f"Solving for size {size-1}")

    step_size = 1
    stats = {}
    while not ctl.solve(on_model=on_model).satisfiable:
        start_size = size
        stats[size - 1] = ctl.statistics["summary"]["times"]
        try_new = True
        if use_cautious_generate:
            added = create_from_cautious(ctl, size)
            size += added
            try_new = added == 0
        while try_new:
            ground(ctl, size, "object")
            size += 1
            if size > start_size + step_size:
                try_new = False
        print(f"Solving for size {size-1}")

    stats[size - 1] = ctl.statistics["summary"]["times"]

    end = time.time()

    out_name = f"benchmarks/latest/{generate_output_path(args)}"
    if args.cautious:
        out_name += "-c"
    if args.cautious_assoc:
        out_name += "-ca"

    with open(f"{out_name}.txt", "w") as f:
        print(json.dumps(stats, indent=4), file=f)
        print("TOTAL TIME: ", sum([r["total"] for r in stats.values()]), file=f)
        print("TOTAL SOLVE TIME: ", sum([r["solve"] for r in stats.values()]), file=f)
        print("Actual TIME: ", end - start, file=f)
