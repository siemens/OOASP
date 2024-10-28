from ooasp.smart_ooasp import SmartOOASPSolver
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

import os

global solver, setup_flag, st, allowed_objects, allowed_associations

FE_ORIGINS = ['http://localhost:5173']

SMART_FUNCTIONS = ["association_possible", "assoc_needs_object", "global_lb_gap", "global_ub_gap"]

solver = SmartOOASPSolver(smart_generation_functions=SMART_FUNCTIONS)
# check brave cons. here not in Solver
setup_flag = False
st = ""
allowed_objects = []
allowed_associations = {}
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=FE_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_known_names(kb_path):
    global allowed_objects
    allowed_objects = []
    with open(kb_path, "r+") as f:
        facts = f.read().strip().replace("\n","").replace("\r","").split(".")
        for fact in facts:
            if "%" in fact:
                continue
            if "ooasp_class" in fact:
                class_name = fact.split("(")[1][0:-1] 
                allowed_objects.append(class_name)
    return Response("Allowed Names.", data=allowed_objects)

def load_known_associations(kb_path):
    global allowed_associations
    allowed_associations = {}
    with open(kb_path, "r+") as f:
        facts = f.read().strip().replace("\n","").replace("\r","").split(".")
        for fact in facts:
            if "%" in fact:
                continue
            if "ooasp_assoc(" in fact:
                contents = fact.split("(")
                assoc_info = contents[1].replace(")","").split(",")
                print(assoc_info)
                allowed_associations.update({
                    assoc_info[0]: {
                        "from": assoc_info[1],
                        "fromMin": assoc_info[2],
                        "fromMax": assoc_info[3],
                        "to": assoc_info[4],
                        "toMin": assoc_info[5],
                        "toMax": assoc_info[6]
                    }
                })
    return Response("Allowed Associations.", data=allowed_associations)

def initialise_solver(solver, data):
    object_list = data.objects.split(",") if data.objects != "" else []
    data.prio_associations = data.prio_associations.split(",")
    solver.ctl.load(data.domain)
    solver.initial_objects =  object_list
    solver.associations_with_priority = data.prio_associations

    solver.load_base()
    solver.create_initial_objects()

    global setup_flag
    setup_flag = True

    load_known_associations(data.domain)
    load_known_names(data.domain)
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
    data = {
        "nodes": [],
        "edges": []
    }

    global solver
    known = list(solver.assumptions)
    for assumption in known:
        if "ooasp_isa(" in assumption:
            data_list = assumption.replace(")","").replace("ooasp_isa(","").split(",")
            node = {"object_id":data_list[1], "class":data_list[0]}
            data["nodes"].append(node)
        elif "ooasp_associated(" in assumption:
            data_list = assumption.replace(")","").replace("ooasp_associated(","").split(",")
            edge = {"assoc":data_list[0], "source":data_list[1], "target":data_list[2]}
            data["edges"].append(edge)
    return data

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

@app.get("/graph/assumptions")
async def known():
    graph_repr = represent_as_graph()
    return Response("Success",graph_repr).build()

@app.post("/knowledgebase/{path}")
async def read_kb(path):
    path =  os.path.join(*path.split("-"))
    assoc = load_known_associations(path)
    cls = load_known_names(path)
    return {"classes": assoc, "associations":cls}

@app.get("/knowledgebase")
async def show_loaded_kb():
    global allowed_associations, allowed_objects
    return Response("Known class names and associations.", {"classes": allowed_objects, "associations": allowed_associations})

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

@app.put("/add/{cls}")
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
    return Response("Current assumptions.", data=str(solver.assumptions)).build()

@app.post("/associate/{id1}/{name}/{id2}")
async def associate(id1, id2, name):
    """
    Creates an association between two objects.
    """
    global allowed_associations
    if name not in allowed_associations.keys():
        return Response("This association is not defined in the domain's knowledgebase.", data=allowed_associations).build(code=status.HTTP_400_BAD_REQUEST)

    global solver
    solver.associate((name,int(id1), int(id2)))
    succ =  f"ooasp_associated({name},{id1},{id2})" in solver.assumptions
    return Response("Succesfully added." if succ else "Error while adding.",data=solver.assumption_list).build(code=status.HTTP_200_OK if succ else status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.get("/consequences/cautious")
async def get_cautious():
    """
    Returns cautions consequences.
    These are things true in all models, meaning that these steps must be taken in order to get the result
    """
    global solver
    csq = str(solver.get_cautious()).split(",")
    return Response("Cautious consequences (must haves)", str(csq))

@app.get("/consequences/brave")
async def get_brave():
    """
    Returns brave consequences.
    These are things true in at least one model, meaning that these are suggestions.
    """
    global solver
    csq = str(solver.get_brave()).split(",")
    return Response("Brave consequences (possibilities)", str(csq))

@app.get("/solution/view/{name}")
async def get_diagram(name):
    global solver
    solver.save_png(name=name, extra_prg="_clinguin_browsing.")
    return Response(f"File saved in ./out/{name}.png",data=None).build()