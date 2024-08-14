import json

import time
from argparse import ArgumentParser

from clingo import Control, Number, Function
from clingo import parse_term
import ooasp.settings as settings
from ooasp.utils import red, green, title, subtitle, colored, COLORS


from clingraph.orm import Factbase
from clingraph.graphviz import compute_graphs, render
from clingraph.clingo_utils import ClingraphContext

config = []


class OOASPRacksSolver:

    def __init__(self, args, smart_generation_functions=None):
        self.args = args
        self.ctl = Control(
            [
                "1",
                "--warn=none",
                f"-c config_name=c1",
                f"-c kb_name=k1",
                "-t3",
                "--project=show",
            ]
        )
        self.ctl.load("examples/racks/kb.lp")
        self.ctl.load("ooasp/encodings/ooasp_simple.lp")

        self.ctl.ground([("base", [])])
        self.ctl.solve()
        self.next_id = 1
        self.associations = []
        self.model = None
        self.cautious = None
        self.brave = None

        if smart_generation_functions is None:
            self.smart_generation_functions = [
                "lb_at_least",
                "upper_filled",
                "lower_global",
                "association_needed_lb",
            ]
        else:
            self.smart_generation_functions = smart_generation_functions

        def log(*args):
            if self.args.verbose:
                print(*args)
            pass

        self.log = log

    @property
    def assumptions(self):
        return [(parse_term(a), True) for a in self.associations]

    @classmethod
    def get_parser(cls) -> ArgumentParser:
        """
        Return the parser for command line options.
        """
        parser = ArgumentParser(
            prog="ooasp",
        )
        parser.add_argument("--verbose", action="store_true")
        parser.add_argument("--view", action="store_true")
        # ------------------------Smart generation options ------------------------
        parser.add_argument("--cautious", action="store_true")
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

    def create_initial_objects(self):
        initial_objects = []

        initial_objects += ["frame"] * self.args.frame

        initial_objects += ["rackDouble"] * self.args.rackDouble
        initial_objects += ["rackSingle"] * self.args.rackSingle
        initial_objects += ["rack"] * self.args.rack

        initial_objects += ["elementA"] * self.args.elementA
        initial_objects += ["elementB"] * self.args.elementB
        initial_objects += ["elementC"] * self.args.elementC
        initial_objects += ["elementD"] * self.args.elementD
        initial_objects += ["element"] * self.args.element

        initial_objects += ["module"] * self.args.module
        initial_objects += ["moduleI"] * self.args.moduleI
        initial_objects += ["moduleII"] * self.args.moduleII
        initial_objects += ["moduleIII"] * self.args.moduleIII
        initial_objects += ["moduleIV"] * self.args.moduleIV
        initial_objects += ["moduleV"] * self.args.moduleV

        for o in initial_objects:
            self.add_object(o)

    def ground(self, o):
        self.log(f"\t\tGrounding {self.next_id} {o}")
        self.ctl.ground([("domain", [Number(self.next_id), Function(o, [])])])
        if self.next_id > 0:
            self.ctl.release_external(Function("active", [Number(self.next_id - 1)]))
        self.ctl.assign_external(Function("active", [Number(self.next_id)]), True)

    def add_object(self, o):
        obj_atom = f"ooasp_isa({o},{self.next_id})"
        self.log(green(f"\t\tAdding object  {obj_atom}"))
        self.ctl.add("domain", [str(self.next_id), "object"], f"user({obj_atom}).")
        config.append(obj_atom)
        config.append(f"user({obj_atom})")
        self.ground(o)
        self.next_id += 1
        self.cautious = None
        self.brave = None

    def add_association(self, association):
        assoc_atom = (
            f"ooasp_associated({association[0]},{association[1]},{association[2]})"
        )
        self.log(green(f"\t\tAdding association  {assoc_atom}"))
        self.associations.append(assoc_atom)
        self.cautious = None
        self.brave = None

    def get_cautious(self):
        if self.cautious:
            return self.cautious
        self.ctl.assign_external(Function("check_potential_cv"), False)
        self.ctl.assign_external(Function("computing_cautious"), True)
        self.ctl.configuration.solve.models = "0"
        self.ctl.configuration.solve.enum_mode = "cautious"
        with self.ctl.solve(yield_=True, assumptions=self.assumptions) as hdn:
            for model in hdn:
                self.cautious = model.symbols(shown=True)
            if self.cautious is None:
                self.log("\tUNSAT cautious!")
        self.ctl.assign_external(Function("check_potential_cv"), True)
        self.ctl.assign_external(Function("computing_cautious"), False)
        self.ctl.configuration.solve.models = "1"
        self.ctl.configuration.solve.enum_mode = "auto"
        self.ctl.configuration.solve.project = "auto"
        return self.cautious

    def get_brave(self):
        if self.brave:
            return self.brave
        self.ctl.assign_external(Function("check_potential_cv"), False)
        self.ctl.assign_external(Function("computing_brave"), True)
        self.ctl.configuration.solve.models = "0"
        self.ctl.configuration.solve.enum_mode = "brave"
        with self.ctl.solve(yield_=True, assumptions=self.assumptions) as hdn:
            for model in hdn:
                self.brave = model.symbols(shown=True)
            if self.brave is None:
                self.log("\tUNSAT brave!")
        self.ctl.assign_external(Function("check_potential_cv"), True)
        self.ctl.assign_external(Function("computing_brave"), False)
        self.ctl.configuration.solve.models = "1"
        self.ctl.configuration.solve.enum_mode = "auto"
        self.ctl.configuration.solve.project = "auto"
        return self.brave

    def save_png(self, directory: str = "./out"):
        """
        Saves the configuration as a png using clingraph
        """
        config = "\n".join([str(c) + "." for c in self.model])
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
            on_model=lambda m: fbs.append(
                Factbase.from_model(m, default_graph="config")
            )
        )
        graphs = compute_graphs(fbs[0])
        render(
            graphs, format="png", name_format="config", directory=directory, view=True
        )

    def lb_at_least(self):
        self.log("\t+++++ lb_at_least")
        added_key = None
        added = 0
        cautious = self.get_cautious()
        for s in cautious:
            if s.match("lb_at_least", 6):
                o_id, assoc, needed, c, opt, _ = s.arguments
                if added_key is None:
                    self.log("\t  ---> Apply ", s)
                    added_key = (o_id, assoc)
                if added_key != (o_id, assoc):
                    continue
                for _ in range(added, needed.number):
                    if str(opt) == "1":
                        a = (str(assoc), o_id, self.next_id)
                    else:
                        a = (str(assoc), self.next_id, o_id)
                    self.add_object(c.name)
                    self.add_association(a)
                    added += 1
        return added > 0

    def upper_filled(self):
        self.log("\t+++++ upper_filled")
        cautious = self.get_cautious()
        for s in cautious:
            if s.match("upper_filled", 5):
                self.log("\t  ---> Apply ", s)
                _, _, c2, needed, _ = s.arguments
                for _ in range(0, needed.number):
                    self.add_object(c2.name)
                return True
        return False

    def lower_global(self):
        self.log("\t+++++ lower_global")
        cautious = self.get_cautious()
        for s in cautious:
            if s.match("lower_global", 5):
                self.log("\t  ---> Apply ", s)
                c1, _, _, needed, _ = s.arguments
                for _ in range(0, needed.number):
                    self.add_object(c1.name)
                return True
        return False

    def association_needed_lb(self):
        self.log("\t+++++ association_needed_lb")
        brave = self.get_brave()
        for s in brave:
            if s.match("association_needed_lb", 4):
                self.log("\t  ---> Apply ", s)
                assoc, id1, id2, _ = s.arguments
                a = (str(assoc), id1, id2)
                self.add_association(a)
                return True
        return False

    def smart_generation(self):
        self.log(subtitle("Smart generation"))
        initial_size = self.next_id
        initial_associations = len(self.associations)
        for f in self.smart_generation_functions:
            done = getattr(self, f)()
            if done:
                self.log(
                    f"Smart generation: added {self.next_id-initial_size} objects and {len(self.associations)-initial_associations} associations"
                )
                return True
        return False

    def run(self):
        start = time.time()
        self.create_initial_objects()
        done = False

        def on_model(m):
            self.model = [str(s) + "." for s in m.symbols(atoms=True)]

        while not done:
            self.log("\n" + title(f"Next round: {self.next_id-1} objects"))
            things_done = self.smart_generation()
            if things_done:
                continue
            self.log(subtitle(f"Solving for size {self.next_id-1}...", "RED"))
            self.ctl.configuration.solve.models = "1"
            res = self.ctl.solve(on_model=on_model, assumptions=self.assumptions)
            if res.satisfiable:
                done = True
                continue
            self.log(red("No solution found"))
            self.add_object("object")

        end = time.time()

        print("Actual TIME: ", end - start)

        if self.args.view:
            self.save_png()

        print("RUNTIME: ", end - start)


# ========================== Main

if __name__ == "__main__":
    parser = OOASPRacksSolver.get_parser()
    args = parser.parse_args()
    smart_generation_functions = [
        "lower_global",
        "association_needed_lb",
        "upper_filled",
        "lb_at_least",
    ]
    solver = OOASPRacksSolver(
        args, smart_generation_functions=smart_generation_functions
    )
    solver.run()
