from ooasp.smart_ooasp import SmartOOASPSolver
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List

import os

global solver, setup_flag, st

SMART_FUNCTIONS = ["association_possible", "assoc_needs_object", "global_lb_gap", "global_ub_gap"]

solver = SmartOOASPSolver(smart_generation_functions=SMART_FUNCTIONS)
setup_flag = False
st = ""
app = FastAPI()

def initialise_solver(solver, data):
    data.objects = data.objects.split(",")
    data.prio_associations = data.prio_associations.split(",")
    solver.ctl.load(data.domain)
    solver.initial_objects =  data.objects
    solver.associations_with_priority = data.prio_associations

    solver.load_base()
    solver.create_initial_objects()

    global setup_flag
    setup_flag = True

    return Response(message="Solver was initialised.", data=solver.__dict__).build()

def filter_model():
    """
    Takes a list of assumptions or a model formatted as list and filters only relevant atoms.
    """
    pass

def represent_as_graph():
    """
    Represents list of objects and associations a collection of nodes and edges.
    """
    pass

class Response:
    def __init__(self, message, data) -> None:
        self.message = message
        self.data = data
    
    def __repr__(self):
        return str(self.__dict__)
    
    def build(self, additional=None,code=status.HTTP_200_OK):
        content = {
            "message": self.message,
            "data": self.data
        }
        if additional is not None:
            content.update(additional)
        return JSONResponse(content=str(content), status_code=code)

class InitData(BaseModel):
    objects : str = ""
    prio_associations : str = ""
    domain : str = str(os.path.join("examples", "racks", "kb.lp"))

@app.get("/test")
async def add():
    global st
    st = st + "+"
    return st

@app.get("/")
async def activity():
    return Response(setup_flag, None).build()

@app.post("/initialise")
async def init_solver(values: InitData):
    return initialise_solver(solver, values)

@app.post("/add/{cls}")
async def add_object(cls):
    global solver
    solver.add_object(str(cls))
    return Response(f"Added object: {cls}.", data=str(solver.__dict__))


@app.get("/model")
async def get_model():
    global solver
    m = solver.model
    msg  = "No solution available." if m is None else "Current solution found."
    return Response(msg, data=str(m)).build()

@app.post("/solve")
async def call_solve():
    global solver
    solver.smart_complete()
    return Response("Generated a solution.", data=str(solver.model)).build()

@app.get("/objects")
async def get_all_objects():
    global solver
    return Response("Current objects.", data=str(solver.objects)).build()

@app.get("/assumptions")
async def get_all_assumptions():
    global solver
    return Response("Current assumptions.", data=str(solver.assumption_list)).build()

@app.post("/associate/{id1}/{name}/{id2}")
async def associate(id1, id2, name):
    """
    Creates an association between two objects.
    """
    global solver
    solver.associate((name,int(id1), int(id2)))
    succ =  f"ooasp_associated({name},{id1},{id2})" in solver.assumptions
    return Response("Succesfully added." if succ else "Error while adding.",data=solver.assumption_list).build(code=status.HTTP_200_OK if succ else status.HTTP)

@app.get("/consequences/cautious")
async def get_cautious():
    """
    Returns cautions consequences.
    These are things true in all models, meaning that these steps must be taken in order to get the result
    """
    pass

@app.get("consequences/brave")
async def get_brave():
    """
    Returns brave consequences.
    These are things true in at least one model, meaning that these are suggestions.
    """
    pass


@app.get("/solution/view/{name}")
async def get_diagram(name):
    global solver
    solver.save_png(name=name, extra_prg="_clinguin_browsing.")
    return Response(f"File saved in ./out/{name}.png",data=None).build()