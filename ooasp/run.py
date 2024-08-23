from argparse import ArgumentParser
import time
import threading
from clingo import Control, Number, Function
from clingo import parse_term
from clingo.symbol import Symbol
import ooasp.settings as settings
from ooasp.utils import red, green, title, subtitle, pretty_dict


from clingraph.orm import Factbase
from clingraph.graphviz import compute_graphs, render
from clingraph.clingo_utils import ClingraphContext


CLASSES = [
    "object",
    "element",
    "rack",
    "module",
    "frame",
    "rackSingle",
    "rackDouble",
    "elementA",
    "elementB",
    "elementC",
    "elementD",
    "moduleI",
    "moduleII",
    "moduleIII",
    "moduleIV",
    "moduleV",
]

SMART_FUNCTIONS = {
    "object_needed": {"type": "cautious", "arity": 6},
    "global_ub": {"type": "cautious", "arity": 3},
    "global_lb": {"type": "cautious", "arity": 3},
    "association_needed": {"type": "brave", "arity": 4},
}


def get_parser() -> ArgumentParser:
    """
    Return the parser for command line options.
    """
    parser = ArgumentParser(
        prog="ooasp",
    )
    # ------------------------General------------------------
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "--view",
        action="store_true",
        help="Saves the solution as a PNG generated by clingraph",
    )
    # ------------------------Smart generation options ------------------------
    parser.add_argument("--timeout", type=int, help="Timeout in seconds")
    parser.add_argument(
        "--smart-generation",
        type=str,
        help=f"""Specifies what functions for smart generation to use.
                    Possible options: {list(SMART_FUNCTIONS.keys())}.
                    Input has to be comma-separated list.
                    Functions are executed in the order specified.""",
    )
    # ------------------------Initial objects------------------------
    for c in CLASSES:
        parser.add_argument(f"--{c}", type=int, default=0, help=f"Number of {c}s")
    return parser


class OOASPRacksSolver:
    """
    Solver for the OOASP using the racks problem as example.
    The approach is generalizable to other problems.
    """

    def __init__(
        self,
        initial_objects=None,
        smart_generation_functions=None,
        verbose=False,
        view=False,
        timeout=1200,
    ):
        """
        Initialize the solver.

        Args:
            initial_objects (list): List of initial objects to start with.
            smart_generation_functions (list): List of smart generation functions to use for incremental generation.
            verbose (bool): Verbose output will show the logs
            view (bool): If True, saves the solution as a PNG generated by clingraph
            timeout (int): Timeout in seconds
        """
        self.initial_objects = initial_objects if initial_objects is not None else []
        self.smart_generation_functions = (
            smart_generation_functions if smart_generation_functions is not None else []
        )
        self.view = view
        self.timeout = timeout

        self.ctl = Control(
            [
                "1",
                "--warn=none",
                "-c config_name=c1",
                "-c kb_name=k1",
                "-t3",
                "--project=show",
            ]
        )
        self.ctl.load("examples/racks/kb.lp")
        self.ctl.load("ooasp/encodings/ooasp_simple.lp")

        self.ctl.ground([("base", [])])
        self.timeout_reached = False
        self.next_id = 1
        self.associations = []
        self.object_atoms = []
        self.model = None
        self.shown_model = None
        self.cautious = None
        self.brave = None
        self.times = {
            "runtime": 0,
            "initialization": 0,
            "smart_generation": {
                "time": 0,
                "cautious": 0,
                "brave": 0,
                "functions": {n: 0 for n in smart_generation_functions},
            },
            "solve": 0,
            "ground": 0,
        }
        self.objects = {c: 0 for c in CLASSES}

        def log(*args):
            if verbose:
                print(*args)

        self.log = log

    @property
    def stats(self):
        """
        Returns the statistics of the run.
        """

        times = {
            "runtime": round(self.times["runtime"], 3),
            "initialization": round(self.times["initialization"], 3),
            "smart_generation": {
                "time": round(self.times["smart_generation"]["time"], 3),
                "cautious": round(self.times["smart_generation"]["cautious"], 3),
                "brave": round(self.times["smart_generation"]["brave"], 3),
                "functions": {
                    k: round(v, 3)
                    for k, v in self.times["smart_generation"]["functions"].items()
                },
            },
            "solve": round(self.times["solve"], 3),
            "ground": round(self.times["ground"], 3),
        }
        considered_coseq = {"cautious": False, "brave": False}
        for f in self.smart_generation_functions:
            conseq_type = SMART_FUNCTIONS[f]["type"]
            if not considered_coseq[conseq_type]:
                considered_coseq[conseq_type] = True
                times["smart_generation"]["functions"][f] = round(
                    (
                        times["smart_generation"]["functions"][f]
                        - times["smart_generation"][conseq_type]
                    ),
                    3,
                )
        results = {
            "timeout": self.timeout_reached,
            "#objects": self.next_id - 1,
            "#objects_added_per_type": {k: v for k, v in self.objects.items() if v > 0},
            "#associations": len(self.associations),
            "times": times,
            "model": (
                None
                if not self.model
                else [
                    s
                    for s in self.model
                    if s.startswith("ooasp_isa_leaf")
                    or s.startswith("ooasp_associated")
                ]
            ),
        }
        return results

    @property
    def assumptions(self):
        """
        List of assumptions for the solver. All associations are used as assumptions.
        """
        return [(parse_term(a), True) for a in self.associations]

    def create_initial_objects(self):
        """
        Creates the initial objects based on the input parameter by adding and grounding the objects.
        """
        for o in self.initial_objects:
            self.add_object(o)

    def ground(self, o: str):
        """
        Grounds the program corresponding to the new object.
        It also releases the external for the previous object and assigns the new object as active
        to account for the current point in the incremental grounding.

        Args:
            o (str): The name of the class of the object to ground.
        """
        self.log(f"\t\tGrounding {self.next_id} {o}")
        start = time.time()
        self.ctl.ground([("domain", [Number(self.next_id), Function(o, [])])])
        self.times["ground"] += time.time() - start
        if self.next_id > 0:
            self.ctl.release_external(Function("active", [Number(self.next_id - 1)]))
        self.ctl.assign_external(Function("active", [Number(self.next_id)]), True)

    def add_object(self, o: str):
        """
        Adds a new object to the configuration. This addition includes the user predicate
        to know the class for the object that was added and distinguish it in the encodings.

        Args:
            o (str): The name of the class of the object to ground.
        """
        obj_atom = f"ooasp_isa({o},{self.next_id})"
        dom_atom = f"ooasp_domain({o},{self.next_id})"
        self.log(green(f"\t\tAdding object  {obj_atom}"))
        self.ctl.add("domain", [str(self.next_id), "object"], f"user({obj_atom}).")
        self.ctl.add("domain", [str(self.next_id), "object"], f"{obj_atom}.")
        self.ctl.add("domain", [str(self.next_id), "object"], f"{dom_atom}.")
        self.object_atoms.append(obj_atom)
        self.object_atoms.append(dom_atom)
        self.objects[o] += 1
        self.ground(o)
        self.next_id += 1
        self.cautious = None
        self.brave = None

    def add_association(self, association: tuple[str, int, int]):
        """_summary_
        Associates two objects with a given association.
        Args:
            association (tuple[str, int, int]): The association to add. The tuple contains the name of the association and the ids of the two objects to associate.
        """
        assoc_atom = (
            f"ooasp_associated({association[0]},{association[1]},{association[2]})"
        )
        self.log(green(f"\t\tAdding association  {assoc_atom}"))
        self.associations.append(assoc_atom)
        self.cautious = None
        self.brave = None

    def get_cautious(self) -> list[Symbol]:
        """
        Obtains and stores the cautious consequences of the current configuration.

        Returns:
            list[clingo.Symbol]: List of symbols representing the cautious consequences.
        """
        if self.cautious:
            return self.cautious
        start = time.time()
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
        self.times["smart_generation"]["cautious"] += time.time() - start
        return self.cautious

    def get_brave(self) -> list[Symbol]:
        """
        Obtains and stores the brave consequences of the current configuration.

        Returns:
            list[clingo.Symbol]: List of symbols representing the brave consequences.
        """

        if self.brave:
            return self.brave
        start = time.time()
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
        self.times["smart_generation"]["brave"] += time.time() - start
        return self.brave

    def save_png(self, directory: str = "./out", suffix: str = ""):
        """
        Saves the configuration as a png using clingraph
        Args:
            directory (str): The directory to save the png
            suffix (str): The suffix to add to the name of the png
        """
        if self.model:
            config = "\n".join([str(c) for c in self.model])
        else:
            config = "\n".join(
                [str(c) + "." for c in self.object_atoms + self.associations]
            )
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
            graphs,
            format="png",
            name_format="config" + suffix,
            directory=directory,
            view=True,
        )

    # ------------------------Smart Generation------------------------

    def smart_generation(self) -> bool:
        """
        Calls the smart generation functions in the order specified by the user.
        It will stop once a function adds objects or associations.

        Returns:
            bool: True if any of the smart generation functions added objects or associations, False otherwise.
        """
        self.log(subtitle("Smart generation"))
        initial_size = self.next_id
        initial_associations = len(self.associations)
        for f in self.smart_generation_functions:
            start = time.time()
            done = getattr(self, f)()
            self.times["smart_generation"]["functions"][f] += time.time() - start
            if done:
                self.log(
                    f"Smart generation: added {self.next_id - initial_size} objects and {len(self.associations) - initial_associations} associations"
                )
                return True
        return False

    def object_needed(self) -> bool:
        """
        The appearance of predicate object_needed(ID1, ASSOC, X, C2, OPT, new_object)
        in the cautious consequences indicates the need to add
        at least X objects of type C2 which can be immediately associated to object ID1.

        We choose the first appearance of this predicate and add the needed objects
        for the selected object and association until the needed number of needed objects is reached.

        Returns:
            bool: True if objects were added, False otherwise
        """
        self.log("\t+++++ object_needed")
        added_key = None
        added = 0
        cautious = self.get_cautious()
        for s in cautious:
            if s.match("object_needed", 6):
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

    def global_ub(self) -> bool:
        """
        The appearance of predicate global_ub(C2, X, new_object)
        in the cautious consequences indicates the need to add N objects of type C2

        Given a target association ASSOC where each C2 can be associated to at most MAX objects of C1
        and each C1 has to be associated to exactly one C2.
        We count the global number of objects of class C2 and this is not enough to cover all C2 objects
        therefore the upper bound of classes C2 was already reached and we need to add N objects of class C2
        to fill the gap.

        Returns:
            bool: True if objects were added, False otherwise
        """
        self.log("\t+++++ global_ub")
        cautious = self.get_cautious()
        for s in cautious:
            if s.match("global_ub", 3):
                self.log("\t  ---> Apply ", s)
                c2, needed, _ = s.arguments
                for _ in range(0, needed.number):
                    self.add_object(c2.name)
                return True
        return False

    def global_lb(self) -> bool:
        """
        The appearance of predicate global_lb(C1, X, new_object)
        in the cautious consequences indicates the need to add N objects of type C1

        Given a target association ASSOC where each C2 can be associated to at least MIN objects of C1
        and each C1 has to be associated to exactly one C2.
        We count the global number of objects of class C1 and this is not enough to cover all C2 lowe bounds.
        Therefore the lower bound of classes C2 cant be filled and we need to add N objects of class C1.
        to fill the gap.

        Returns:
            bool: True if objects were added, False otherwise
        """
        self.log("\t+++++ global_lb")
        cautious = self.get_cautious()
        for s in cautious:
            if s.match("global_lb", 3):
                self.log("\t  ---> Apply ", s)
                c1, needed, _ = s.arguments
                for _ in range(0, needed.number):
                    self.add_object(c1.name)
                return True
        return False

    def association_needed(self) -> bool:
        """
        The appearance of predicate association_needed(ASSOC, ID1, ID2, new_object)
        in the brave consequences indicates the need to add an association between two objects.

        We know that ID1 needs at least one object of class C1 and ID2 needs at least one object of class C2
        We know that the objects ID1 and ID2 can potentially be associated by ASSOC
        We also know that the classes of these objects was set byt the user or the smart association.
        This makes sure that the association added does not determine the classes of the objects if not previously given

        Returns:
            bool: True if associations were added, False otherwise
        """
        self.log("\t+++++ association_needed")
        brave = self.get_brave()
        for s in brave:
            if s.match("association_needed", 4):
                self.log("\t  ---> Apply ", s)
                assoc, id1, id2, _ = s.arguments
                a = (str(assoc), id1, id2)
                self.add_association(a)
                return True
        return False

    def run(self):
        """
        Runs the solver.
        It starts by creating the initial objects and then iterates over the smart generation and solving steps.
        It stops when a solution is found or the timeout is reached.
        If the view is enabled, it saves the solution as a PNG.
        """
        run_start = time.time()
        self.create_initial_objects()
        self.times["initialization"] = time.time() - run_start
        done = False

        def on_model(m):
            self.model = [str(s) + "." for s in m.symbols(atoms=True)]

        round = 0
        while not done and not self.timeout_reached:
            round += 1
            self.log("\n" + title(f"Next round: {self.next_id - 1} objects"))
            if self.view:
                self.save_png("out/solve", f"-O{self.next_id-1}-round{round}")
            start = time.time()
            things_done = self.smart_generation()
            self.times["smart_generation"]["time"] += time.time() - start
            if things_done:
                continue
            self.log(subtitle(f"Solving for size {self.next_id - 1}...", "RED"))
            self.ctl.configuration.solve.models = "1"
            start = time.time()
            with self.ctl.solve(
                assumptions=self.assumptions, async_=True, on_model=on_model
            ) as hdl:
                time_left = self.timeout - (time.time() - run_start)
                if hdl.wait(time_left):
                    self.times["solve"] += time.time() - start
                    if hdl.get().satisfiable:
                        self.log(green("SAT"))
                        done = True
                    else:
                        self.log(red("UNSAT"))
                        self.add_object("object")
                    continue
                self.log("Timeout reached")
                hdl.cancel()

            self.times["solve"] += time.time() - start
            self.timeout_reached = True

        self.times["runtime"] = time.time() - run_start

        print(pretty_dict(self.stats))
        if self.view:
            self.save_png("out/solve", f"-O{self.next_id-1}-R-{round+1}")
            self.save_png()


# ========================== Main

if __name__ == "__main__":
    cmd_args = get_parser().parse_args()

    initial = []
    for cls in CLASSES:
        initial += [cls] * getattr(cmd_args, cls)

    if cmd_args.smart_generation is not None:
        smart_functions = [f.strip() for f in cmd_args.smart_generation.split(",")]
    else:
        smart_functions = []

    solver = OOASPRacksSolver(
        initial_objects=initial,
        smart_generation_functions=smart_functions,
        verbose=cmd_args.verbose,
        view=cmd_args.view,
        timeout=cmd_args.timeout,
    )
    solver.run()
