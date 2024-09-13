from clinguin.server.application.backends import ClingraphBackend
from ooasp.smart_ooasp import SmartOOASPSolver
from clingo import Function, Control, parse_term


SAVE_FILE = "ooasp_configuration.lp"


ASSOCIATION_SPECIALIZATIONS = [
    "rack_framesS",
    "rack_framesD",
    "element_modules1",
    "element_modules2",
    "element_modules3",
    "element_modules4",
]


class OOASPBackend(ClingraphBackend):

    def _init_ctl(self):
        super()._init_ctl()
        self.smart_solver = SmartOOASPSolver(
            initial_objects=[],
            ctl=self._ctl,
            verbose=True,
            associations_with_priority=ASSOCIATION_SPECIALIZATIONS,
            smart_generation_functions=[
                "object_needed",
                "global_lb",
                "global_ub",
                "association_needed",
            ],
        )
        self.smart_solver.load_base()
        # self.smart_solver.create_initial_objects()
        self._set_external(Function("check_potential_cv"), "false")

    @property
    def _assumption_list(self):
        return super()._assumption_list.union(self.smart_solver.assumption_list)

    def _prepare(self):
        # self.smart_solver.ctl.assign_external(Function("check_potential_cv"), False)
        pass

    def _add_assumption(self, symbol, value="true"):
        # Overwrites
        super()._add_assumption(symbol, value)
        self.smart_solver.assumptions.add(str(symbol))

    # ------ Operations

    def add_object(self, name, amount=1):
        must_be_used = name != "object"
        print(must_be_used)
        for obj in range(int(amount)):
            # We force the use of the object to improve performance
            self.smart_solver.add_object(name, must_be_used=must_be_used)
        self._outdate()
        self._set_external(Function("check_potential_cv"), "false")

    def remove_assumption(self, atom):
        super().remove_assumption(atom)
        if atom in self.smart_solver.assumptions:
            self.smart_solver.assumptions.remove(atom)

    def find_incrementally(self):
        """
        Finds the next solution incrementally.
        """
        self._outdate()
        self._set_external(Function("check_potential_cv"), "true")
        self.smart_solver.smart_complete()
        self.next_solution()  # Called so that we start browsing automatically

    def import_solution(self, f_path=SAVE_FILE):
        """
        Takes a file containing a configuration encoding and loads it into the editor.
        """
        f_path = f_path.strip("\"") # It seems that passing the argument from the clinguin adds extra quotes which need to be removed
        self._restart()
        ctl = Control(["1"])
        ctl.load(f_path)
        ctl.ground([("base", [])])
        model = None
        objects = {}
        assumptions = []
        with ctl.solve(yield_=True) as handle:
            for model in handle:
                for atom in model.symbols(atoms=True):
                    assumptions.append(str(atom))
                    if atom.match("ooasp_isa", 2):
                        atom.arguments
                        objects[atom.arguments[1].number] = atom.arguments[0].name
                model = model.symbols(atoms=True)
        objects = dict(sorted(objects.items(), key=lambda x: x[0]))
        for expected_next_id, c in objects.items():
            while expected_next_id > self.smart_solver.next_id:
                self.smart_solver.add_object("object", must_be_used=False)
            self.smart_solver.add_object(c, must_be_used=True)
        for a in assumptions:
            self._add_assumption(parse_term(a))
