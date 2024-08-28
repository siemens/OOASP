import sys
import textwrap
from typing import Sequence

import clingo
from clingo import Control
from clingo import Flag, ApplicationOptions

from ooasp.smart_ooasp import SmartOOASPSolver, SMART_FUNCTIONS
import os

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

# TODO if this improves the performance, we can obtain this associations from the encoding
ASSOCIATION_SPECIALIZATIONS = [
    "rack_framesS",
    "rack_framesD",
    "element_modules1",
    "element_modules2",
    "element_modules3",
    "element_modules4",
]


class OOASPRacksApp(clingo.Application):
    """
    Application class for solving the racks problem using OOASP.
    """

    def __init__(self, name):
        """
        Create application
        """
        self.program_name = name
        self._view = Flag()
        self._debug = Flag()
        self._initial_objects = []
        self._smart_functions = []

    def parse_log_level(self, log_level):
        """
        Parse log
        """
        if log_level is not None:
            self._log_level = log_level.upper()
            return self._log_level in ["INFO", "WARNING", "DEBUG", "ERROR"]

        return True

    def parse_scale(self, scale):
        """
        Parse scale
        """
        if scale is not None:
            self._scale = float(scale)

        return True

    def parse_smart_functions(self, smart_functions):
        """
        Parse smart generation functions
        """
        self._smart_functions = [f.strip() for f in smart_functions.split(",")]

        return True

    def meta_parse_object(self, class_name):
        """
        Wrapper function to parse the number of objects of a class
        """

        def parser(value):
            try:
                value = int(value)
            except ValueError:
                return False
            self._initial_objects += [class_name] * value
            return True

        return parser

    def register_options(self, options: ApplicationOptions) -> None:
        """
        Add custom options
        """
        group = "Clingo.SmartOOASP"
        options.add(
            group,
            "smart-functions",
            textwrap.dedent(
                f"""\
                The smart_functions used for smart generation.
                Must be a string separated with "," using: {",".join(SMART_FUNCTIONS.keys())}
                """
            ),
            self.parse_smart_functions,
            argument="<smart_functions>",
        )
        options.add_flag(
            group, "view", "Visualize the first solution using clingraph", self._view
        )
        options.add_flag(group, "debug", "Show debug output with steps", self._debug)
        for cls in CLASSES:
            options.add(
                group,
                cls,
                f"Number of {cls}s",
                self.meta_parse_object(cls),
                argument="<number>",
            )

    def main(self, ctl: Control, files: Sequence[str]) -> None:
        """
        Runs the solver.
        It starts by creating the initial objects and then iterates over the smart generation and solving steps.
        It stops when a solution is found.
        If the view is enabled, it saves the solution as a PNG.
        """
        smartOOASPSolver = SmartOOASPSolver(
            self._initial_objects,
            self._smart_functions,
            self._debug,
            self._view,
            ctl,
            associations_with_priority=ASSOCIATION_SPECIALIZATIONS,
        )
        ctl.load(os.path.join("examples", "racks", "kb.lp"))
        smartOOASPSolver.load_base()
        smartOOASPSolver.create_initial_objects()
        smartOOASPSolver.smart_complete()

        if self._view:
            smartOOASPSolver.save_png()


# ========================== Main

if __name__ == "__main__":

    clingo.clingo_main(OOASPRacksApp("SmartOOASP"), sys.argv[1:])
