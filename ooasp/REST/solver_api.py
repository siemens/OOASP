import random
from ooasp.smart_ooasp import SmartOOASPSolver
from ooasp.REST.file_manager.ProjectManagerInterface import *
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import threading

import os

global solver, setup_flag, st, allowed_objects, allowed_associations, allowed_attributes, selected_domain, action_history
global user_additions, solve_semaphore, active_objects


# TODO FIX BUG WHERE THE SOLVER CANNOT BE REINITIALISED -> full reset required

FE_ORIGINS = ['http://localhost:5173']

SMART_FUNCTIONS = ["association_possible", "assoc_needs_object", "global_lb_gap", "global_ub_gap"]

active_objects=[]
solve_semaphore = False
solver = SmartOOASPSolver(smart_generation_functions=SMART_FUNCTIONS)
# check brave cons. here not in Solver
setup_flag = False
st = ""
allowed_objects = []
allowed_associations = {}
allowed_attributes = []
selected_domain = None
action_history = []
user_additions = []
app = MyAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=FE_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def validate_additions():
    """
    Checks wether IDs and objects in local memory correspond to the ones in current assumptions. 
    """
    pass

def check_call_viability(call,type='class'):
    """
    Checks if a choice to add an object or an association can be done without breaking the system.
    Note: attr is not needed here, as the intention is that it will be used just to generate the node display
    """
    global selected_domain
    if type=="class":
        global allowed_objects
        if call in allowed_objects:
            return (True, "Allowed.")
        return (False, f"Object {call} is not defined within '{selected_domain}' domain.")
    if type == "assoc":
        global allowed_associations
        if call[1] in list(allowed_associations.keys()):
            # TODO IMPORTANT -> find a way to track ids to perform checks on particular objects
            if allowed_associations[call[1]]["from"] == call[0] and allowed_associations[call[1]]["to"] == call[2]:
                return (True, "Allowed")
            # TODO in future and a check for reverse assoc (if there is a reverse assoc with some name allow it and return info + correct call)
            return (False, f"{call[1]} is an allowed association, but not between '{call[0]}' and '{call[2]}'.")
        #TODO in future check if there is an alternative assoc
        return (False, f"Association '{call[1]}' is not defined within '{selected_domain}' domain.")

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
    # do this through the control
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

def load_known_attributes(kb_path):
    global allowed_attributes #TODO reconsider naming, known attributes fits better
    with open(kb_path, "r+") as f:
        facts = f.read().strip().replace("\n","").replace("\r","").split(".")
        for fact in facts:
            if "%" in fact:
                continue
            if "ooasp_attr(" in fact:
                stripped = fact.split("(")[1][0:-1]
                class_name, attr, attr_type = stripped.split(",") 
                allowed_attributes.append({"class":class_name, "attribute":attr, "type":attr_type})
    return Response("Attributes.", data=allowed_objects)

def initialise_solver(solver, data): #!
    global selected_domain
    selected_domain = os.path.split(data.domain)[0]


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
    load_known_attributes(data.domain)
    return Response(message="Solver was initialised.", data=solver.__dict__).build()

# TODO find a way to track positions

def _new_attr(node,attr):
    vals = set()
    vals.add(attr["value"])
    node["data"]["attributes"].append({
        "name":attr["name"],
        "values": vals
    })
    return

def represent_as_graph():
    """
    Represents list of objects and associations a collection of nodes and edges.
    """
    global solve_semaphore
    if solve_semaphore:
        return {"nodes":[{"id":"-1", "type":"wNode", "position":{"x":150, "y":150}, "data":{}}], "edges":[]}

    brave = get_possibilities()

    data = {
        "nodes": [],
        "edges": []
    }

    global solver, active_objects
    active_objects = []
    known = list(solver.assumptions)
    for assumption in known:
        if "ooasp_isa(" in assumption:
            data_list = assumption.replace(")","").replace("ooasp_isa(","").split(",")
            active_objects.append(data_list[1])
            node = {"id":data_list[1],
                    "type": "cstNode",
                    "position": {"x": random.randint(20,200), "y": random.randint(20,200)}, 
                    "data":{"class":data_list[0], "object_id":data_list[1], "attributes":[], "assocs":[]}
                    }
            data["nodes"].append(node)
        elif "ooasp_associated(" in assumption:
            data_list = assumption.replace(")","").replace("ooasp_associated(","").split(",")
            edge = {"id": str(data_list[0])+"-"+str(data_list[1])+"-"+str(data_list[2]),"assoc":data_list[0], "source":data_list[1], "target":data_list[2], "type":"smoothstep",
                    "style":{
                        "strokeWidth":2,
                        "stroke": "#00557C"
                    },
                    "data":{
                        "label": data_list[0]
                    },
                        "label": data_list[0]
                    }
            data["edges"].append(edge)

        for attr in brave["attrs"]:
            #extremely inefficient, but i need a prototype
            if attr["object_id"] in active_objects:
                for node in data["nodes"]:
                    if node["id"] == attr["object_id"]:
                        if len(node["data"]["attributes"]) <= 0:
                            _new_attr(node,attr)
                                
                        else:
                            for node_attribute in node["data"]["attributes"]:
                                if attr["name"] == node_attribute["name"]:
                                    node_attribute["values"].add(attr["value"])

                                else:
                                    _new_attr(node,attr)
        
        for assoc in brave["associations"]:
            if assoc["from"] in active_objects:
                for node in data["nodes"]:
                    if node["id"] == assoc["from"]:
                        if assoc not in node["data"]["assocs"]:
                            node["data"]["assocs"].append(assoc)

    return data

def get_possibilities():
    """
    Returns all possible changes in a dictionary format
    """
    res = {"objects":[],"associations":[],"attrs":[], "smart_suggestions":[]} #smart-suggestions currently do not have a pracical use, but might be useful in future
    global solver
    brave = solver.get_brave()

    for consq in brave:
        consq = str(consq)
        if 'ooasp_isa(' in consq:
            stripped = consq.split('(')[1][:-1]
            divided = stripped.split(',')
            res["objects"].append(
                {"id":divided[1], "class":divided[0]}
            )
        elif 'ooasp_associated(' in consq:
            stripped = consq.split('(')[1][:-1]
            divided = stripped.split(',')
            res["associations"].append(
                {"from":divided[1],
                 "to": divided[2],
                 "assoc_name": divided[0]}
            )
        elif 'ooasp_attr_value(' in consq:
            stripped = consq.split('(')[1][:-1]
            divided = stripped.split(',')
            res["attrs"].append(
                {"name":divided[0],
                 "object_id": divided[1],
                 "value": divided[2]}
            )
        else:
            sf_name, data = consq.split("(")
            data = tuple(data[:-1].split(","))
            res["smart_suggestions"].append(
                {"smart_function": sf_name,
                 "data": data}
            )
    return res

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

@app.get("/active_ids")
async def get_active_objects():
    global active_objects
    return Response("Active ids", active_objects).build()

@app.get("/allowed/assoc/{id1}/{name}/{id2}")
async def check_assoc(id1,name,id2):
    stat, msg = check_call_viability((id1,name,id2), type='assoc')
    return Response(msg,stat).build()

@app.get("/allowed/object/{cls}")
async def check_object(cls):
    stat, msg = check_call_viability(cls, type='class')
    return Response(msg,stat).build()

@app.get("/graph/assumptions")
async def known():
    graph_repr = represent_as_graph()
    return Response("Success",graph_repr).build()

@app.get("/json/possibilities")
async def get_possibilities_ep():
    pos =  get_possibilities()
    return Response("Possible acctions to be taken.",pos).build()

@app.post("/knowledgebase/{path}")
#loads in knowledgebase but does not initialise the solver
async def read_kb(path):
    path =  os.path.join(*path.split("-"))
    assoc = load_known_associations(path)
    cls = load_known_names(path)
    attrs = load_known_attributes(path)
    return {"classes": assoc, "associations":cls, "attributes": attrs}

@app.get("/knowledgebase")
async def show_loaded_kb():
    global allowed_associations, allowed_objects, allowed_attributes
    return Response("Known class names and associations.", {"classes": allowed_objects, "associations": allowed_associations, "attributes":allowed_attributes})

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
    return initialise_solver(solver, values) #!

@app.put("/add/{cls}")
async def add_object(cls):
    global solve_semaphore
    if solve_semaphore:
        return Response("Solver is currently busy.", data=[]).build(code=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    global solver
    solver.add_object(str(cls))
    return Response(f"Added object: {cls}.", data=str(solver.__dict__))


@app.get("/model")
async def get_model():
    global solver
    m = solver.model
    msg  = "No solution available." if m is None else "Current solution found."
    return Response(msg, data=str(m)).build()

def solve_threaded():
    global solver, solve_semaphore
    solve_semaphore = True
    print("Started solving")
    solver.smart_complete()
    solve_semaphore = False
    print("Fisnished Solving")

@app.post("/solve")
async def call_solve():
    global solve_semaphore
    t1 = threading.Thread(target=solve_threaded)
    t1.start()
    print(solve_semaphore)
    return Response("Generating a solution.", data=str(solver.model)).build()

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
    global solve_semaphore,allowed_associations
    if solve_semaphore:
        return Response("Solver is currently busy.", data=[]).build(code=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    global allowed_associations
    if name not in allowed_associations.keys():
        return Response("This association is not defined in the domain's knowledgebase.", data=allowed_associations).build(code=status.HTTP_400_BAD_REQUEST)

    global solver
    solver.associate((name,int(id1), int(id2)))
    succ =  f"ooasp_associated({name},{id1},{id2})" in solver.assumptions
    return Response("Succesfully added." if succ else "Error while adding.",data=solver.assumption_list).build(code=status.HTTP_200_OK if succ else status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.get("/consequences/cautious")
#NOT USED
async def get_cautious():
    """
    Returns cautions consequences.
    These are things true in all models, meaning that these steps must be taken in order to get the result
    """
    global solver
    csq = str(solver.get_cautious()).split(",")
    return Response("Cautious consequences (must haves)", str(csq))

@app.get("/consequences/brave")
#NOT USED
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


# ---------- File management ----------

@app.get("/")
#NOT USED
def get_default():
    response = "Hello World!"
    return JSONResponse(status_code=status.HTTP_200_OK, content=response)

@app.get("/all/list")
#NOT USED
def get_datalist():
    """
    Returns a dictionary containing list of all domains and projects
    """
    return JSONResponse(status_code=status.HTTP_501_NOT_IMPLEMENTED, content="not implemented.")

#----------DOMAIN----------

EXAMPLE_FOLDER_OBJECT = {
    "name": "myFolder",
    "path": "whatever/whatever",
    "contents": ["list of all the available configs."]
}


#TODO explore stricter typing for description

class DomainModel(BaseModel):
    name: str

class DomainUpdateModel(BaseModel):
    version: str | None = None
    ENCODING_FNAME: str | None = None
    CONSTRAINTS_FNAME: str | None = None

class DomainDescription(BaseModel):
    description: str

@app.get("/domain_files_location")
def domain_files_path():
    """
    Returns the current default location of domain files
    """
    response = str(app.pfm.domain_path)
    return JSONResponse(status_code=status.HTTP_200_OK, content=response)

@app.get("/domain/check/{name}")
def check_domain(name):
    """
    Returns True if a domain under the name exists, else returns False.
    """
    #TODO implement
    return JSONResponse(status_code=status.HTTP_501_NOT_IMPLEMENTED, content="not implemented.")

@app.post("/domain/new")
def new_domain(domain: DomainModel):
    """
    Creates a new domain and responds with the data about it.
    """
    #TODO change path
    response = app.pfm.new_domain(domain.name)
    return JSONResponse(status_code=status.HTTP_200_OK, content=response)

@app.get("/domain/{domain_name}")
def get_domain(domain_name):
    """
    Returns domain metadata.
    """
    response = app.pfm.get_domain_metadata(domain_name)
    return JSONResponse(status_code=status.HTTP_200_OK, content=response)

@app.get("/domains")
def all_domains():
    """
    Lists all available domains.
    """
    response = app.pfm.get_all_domains()
    return JSONResponse(status_code=status.HTTP_200_OK, content=response)

@app.put("/domain/{domain_name}")
async def update_domain(domain_name, update_data: DomainUpdateModel):
    """
    Updates data on an existing domain.
    """
    response = app.pfm.update_domain(domain_name, update_data.__dict__)
    return JSONResponse(status_code=status.HTTP_200_OK, content=response)

@app.put("/domain/description/{domain_name}")
def update_domain_description(domain_name, desc: DomainDescription):
    response = app.pfm.update_domain_description(domain_name, desc.description)
    return JSONResponse(status_code=status.HTTP_200_OK, content=response)

@app.get("/domain/description/{domain_name}")
def update_domain_description(domain_name):
    response = app.pfm.get_domain_description(domain_name)
    return JSONResponse(status_code=status.HTTP_200_OK, content=response)
    

@app.delete("/domain/{domain_name}")
async def delete_domain(domain_name):
    """
    Deletes an existing domain.
    """
    response = app.pfm.delete_domain(domain_name)
    return JSONResponse(status_code=status.HTTP_200_OK, content=response)

#----------PROJECT----------

class ProjectDataModel(BaseModel):
    domain: str|None = None
    description: str|None = None

class ProjectUpdateModel(BaseModel):
    domain: str|None = None
    description: str|None = None

class NewFile(BaseModel):
    content: str|None =""
    suffix: str|None = ".ooasp"

@app.get("/all_configs")
def all_configs():
    response = app.pfm.list_files_standalone()
    return JSONResponse(status_code=status.HTTP_200_OK, content=response)

@app.get("/project_files_location")
def get_project_location():
    response = str(app.pfm.project_path)
    return JSONResponse(status_code=status.HTTP_200_OK, content=response)

@app.get("/projects")
def get_projects():
    """
    Returns a list of all projects.
    """
    response = []
    all_projects =  app.pfm.list_all_projects()
    for p in all_projects:
        metadata = app.pfm.get_project_metadata(p)
        metadata.update({"files":[]})
        response.append(metadata)

    return JSONResponse(status_code=status.HTTP_200_OK, content=response)

@app.get("/project/{project_name}")
def get_project(project_name):
    """
    Returns metadata of an existing project.
    """
    response = app.pfm.get_project_metadata(project_name)
    return JSONResponse(status_code=status.HTTP_200_OK, content=response)

@app.post("/project/{project_name}") #TODo change routing here and in new domain as well
def new_project(project_name, project_data: ProjectDataModel):
    """
    Creates a new project.
    """
    response = app.pfm.new_project(project_name, project_data.domain, project_data.description)
    return JSONResponse(status_code=status.HTTP_200_OK, content=response)

@app.put("/project/{project_name}")
def update_project(project_name, project_data: ProjectUpdateModel):
    """
    Updates information about an existing project.
    """
    pass

@app.get("/project/check/{name}")
def check_project(name):
    """
    Checks if a project under a specified name exists.
    """
    #TODO implement
    return JSONResponse(status_code=status.HTTP_501_NOT_IMPLEMENTED, content="not implemented.")

@app.delete("/project/{project_name}")
def delete_project(project_name):
    """
    Deletes an existing project.
    """
    response = app.pfm.delete_project(project_name)
    return JSONResponse(status_code=status.HTTP_200_OK, content=response)

@app.post("/project/{name}/new/{file}")
def create_new_file(name, file, specifics: NewFile):
    """
    Creates a new file within the specified project.
    """
    response = app.pfm.new_file(pname=name, name=file, content=specifics.content,suffix=specifics.suffix)
    return JSONResponse(status_code=status.HTTP_200_OK, content=response)

@app.delete("/project/{pname}/{fname}")
def delete_file(fname, pname):
    response = app.pfm.delete_file(fname,pname)
    return JSONResponse(status_code=status.HTTP_200_OK, content=response)

@app.get("/instance_identifier")
def get_instance_id():
    return JSONResponse(app.pfm.run_id)


# ---------- FORMAT SPECIFIC Fns for FE ----------

@app.get("/all")
async def all_information():
    global solve_semaphore
    return({"state":{"nodes":[{"id":"-1", "type":"wNode", "position":{"x":150, "y":150}, "data":{}}], "edges":[]},"brave":{}}if solve_semaphore else {"state": represent_as_graph(),"brave": get_possibilities()})

@app.get("/possibilities/{id}")
def pos_per_id(id):
    res = {
        "associations": [],
        "attributes": [],
        "classes": None,
    }
    all_brave = get_possibilities()
    # check for associations
    for assoc in all_brave["associations"]:
        if assoc["from"] == str(id):
            res["associations"].append(assoc)
    # check for classes -> this can be fixed for now
    # check for attrs
    val_dict = {}
    for attrs in all_brave["attrs"]:
        # transform to format -> {attr_name, values}
        if  attrs["object_id"] == str(id):
            if attrs["name"] not in list(val_dict.keys()):
                val_dict.update({attrs["name"]:set()})
            val_dict[attrs["name"]].add(attrs["value"])
    
    for k in val_dict:
        res["attributes"].append({"name":k, "values":val_dict[k]})
    return res

@app.get("/active_domain")
async def get_active_domain():
    global selected_domain
    return {"res": selected_domain} if selected_domain is not None else {"res":"SOLVER IS NOT INITIALISED"}


"""
# TODO 


1.) implement attribute selection functionality (solver,api,fe)
2.) implement selected attribute value asa part of model
3.) implement saving and loading of images and models

x.) finalise domain and project selection

4.) ??? Smart association (not to be confused with the solver)
    - allow the system to to infer what is the name of the association if both objects are provided
    - this could potentially save time and make sure that the FE does not need to decide on all information
    ---> count number of known association and compare it the the one in the factbase (on violation disallow action)
    ---> on new association check for possibilites of association for provided object and choose one
5.) Figureout how to do positioning
    - this includes overall node representation as a response from the API

    1. create an imaginary matrix to place in nodes by default
    2. alt. extract hierarchy and assign a row to class per level

6.) Extract attribute options
"""