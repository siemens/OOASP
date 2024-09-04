from clinguin.server.application.backends import ClingraphBackend
from ooasp.smart_ooasp import SmartOOASPSolver
from clingo import Function


class OOASPBackend(ClingraphBackend):

    def _init_ctl(self):
        super()._init_ctl()
        self.smart_solver = SmartOOASPSolver(
            initial_objects=["frame", "element"], ctl=self._ctl, verbose=True
        )
        self.smart_solver.load_base()
        # self.smart_solver.create_initial_objects()
        self.smart_solver.ctl.assign_external(Function("check_potential_cv"), False)

    def add_object(self, name):
        self.smart_solver.add_object(name)
        self._outdate()

    def _prepare(self):
        self.smart_solver.ctl.assign_external(Function("check_potential_cv"), False)
