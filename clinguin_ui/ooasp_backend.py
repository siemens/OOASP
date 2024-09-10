from clinguin.server.application.backends import ClingraphBackend
from ooasp.smart_ooasp import SmartOOASPSolver
from clingo import Function


SAVE_FILE = "ui_save_test.lp"


class OOASPBackend(ClingraphBackend):

    def _init_ctl(self):
        super()._init_ctl()
        self.smart_solver = SmartOOASPSolver(
            initial_objects=[], ctl=self._ctl, verbose=True
        )
        self.smart_solver.load_base()
        # self.smart_solver.create_initial_objects()
        self._set_external(Function("check_potential_cv"), "false")

    @property
    def _assumption_list(self):
        return super()._assumption_list.union(self.smart_solver.assumption_list)

    def add_object(self, name, amount=1):
        for obj in range(int(amount)):
            self.smart_solver.add_object(name)
        self._outdate()
        self._set_external(Function("check_potential_cv"), "false")

    def _prepare(self):
        # self.smart_solver.ctl.assign_external(Function("check_potential_cv"), False)
        pass

    def _add_assumption(self, symbol, value="true"):
        # Overwrites
        super()._add_assumption(symbol, value)
        self.smart_solver.assumptions.add(str(symbol))

    def remove_assumption(self, atom):
        print("Super")
        super().remove_assumption(atom)
        print(self.smart_solver.assumptions)
        if atom in self.smart_solver.assumptions:
            self.smart_solver.assumptions.remove(atom)

    def next_complete_solution(self):
        self.smart_solver.ctl.assign_external(Function("check_potential_cv"), True)

    def export_solution(self, f_path=SAVE_FILE):
        """
        Takes current selected solution and saves it as a file.
        """
        print("CALLED EXPORT")

    def find_incrementally(self):
        """
        Finds the next solution incrementally.
        """
        self._outdate()
        self.smart_solver.smart_complete()
        self.next_solution()  # Called so that we start browsing automatically

    def import_solution(self, f_path=SAVE_FILE):
        """
        Takes a file containing a configuration encoding and loads it into the editor.
        """
        # check the size from the file
        # ground for each object in the file
        # add assumptions for all things in file
        # Add this into the API first ad a parameter iin the init ()must add self.values assumptions
        print("CALLED IMPORT")

    def force_restart(self):
        """
        Remove all elements and reset the environment.
        """
        print("FORCING RESTART")
