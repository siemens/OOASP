from smart_ooasp import *
import pytest


@pytest.fixture
def init_solver():
    solver = SmartOOASPSolver(smart_generation_functions=["association_possible", "assoc_needs_object", "global_lb_gap", "global_ub_gap"],
                              initial_objects=["elementA", "moduleII", "elementB", "rack", "object", "frame", "frame"])
    solver.ctl.load(os.path.join("examples", "racks", "kb.lp"))
    solver.load_base()
    solver.create_initial_objects()
    yield solver


def test_initialisation():
    solver = SmartOOASPSolver(smart_generation_functions=["global_lb_gap", "global_ub_gap"])
    assert solver.initial_objects == []
    assert solver.smart_generation_functions != []
    assert solver.associations_with_priority == []
    assert solver.next_id == 1
    assert solver.assumptions == set()
    assert len(solver.times["smart_generation"]["functions"].keys()) == 2


def test_grounding(init_solver):
    solver = init_solver
    assert len(solver.initial_objects) == 7
    for i in range(10):
        # adding more objects to make sure the grounding time will be larger than potential rounding error
        solver.initial_objects.append("element")
    solver.create_initial_objects()
    initial_ground = solver.times["ground"]
    assert initial_ground > 0
    for i in range(20):
        solver.add_object("frame")
    assert initial_ground < solver.times["ground"]


def test_solve(init_solver):
    solver = init_solver
    solver.create_initial_objects()
    solver.smart_complete()
    print(solver.model)
    assert solver.model is not None
