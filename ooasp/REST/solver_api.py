import random
from ooasp.smart_ooasp import SmartOOASPSolver
from ooasp.REST.file_manager.ProjectManagerInterface import *
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from clingo import Control, Function, parse_term
import threading

import os
import copy

global solver, setup_flag, st, allowed_objects, allowed_associations, allowed_attributes, selected_domain, action_history
global user_additions, solve_semaphore, active_objects, specializations, open_configuration_file


# TODO FIX BUG WHERE THE SOLVER CANNOT BE REINITIALISED -> full reset required

FE_ORIGINS = ['http://localhost:5173']

SMART_FUNCTIONS = ["association_possible", "assoc_needs_object", "global_lb_gap", "global_ub_gap"]

specializations={}
active_objects=[]
open_configuration_file = None
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

@app.put("/upload/{path}")
async def test_load(path):
    global open_configuration_file
    try:
        res = import_solution(path)
        open_configuration_file = path
        return res
    except:
        reset_solver()
        return "Error while loading, solver will be reset."


def import_solution(f_path: str = "fe_model.lp") -> None:
        global solver
        """
        Takes a file containing a configuration encoding and loads it into the editor.
        """
        f_path = f_path.strip(
            '"'
        )  # It seems that passing the argument from the clinguin adds extra quotes which need to be removed
        reset_solver()
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
            while expected_next_id > solver.next_id:
                solver.add_object("object", must_be_used=False)
            solver.add_object(c, must_be_used=True)
        for a in assumptions:
            solver.assumptions.add(str(parse_term(a)))

def load_known_names():
    global allowed_objects, solver
    allowed_objects = []
    for fact in solver.model:
        try:
            f, v = fact.split("(")
            if f == "ooasp_leafclass":
                allowed_objects.append(v[0:-2])
        except:
            continue
    return Response("Allowed Names.", data=allowed_objects)

def load_specializations():
    global specializations, solver
    for fact in solver.model:
        if "ooasp_assoc_specialization" in fact:
            print(fact)
            sub,sup = fact.split("(")[1].split(",")
            print(sub,sup)
            if sup[0:-2] in specializations.keys():
                specializations[sup[0:-2]].append(sub)
            else:
                specializations.update({sup[0:-2]:[sub]})
    return specializations


def load_known_associations():
    # do this through the control
    global allowed_associations, solver
    allowed_associations = {}
    for fact in solver.model:
        if "%" in fact:
            continue
        if "ooasp_assoc(" in fact:
            contents = fact.split("(")
            assoc_info = contents[1].replace(")","").replace(".","").split(",")
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

def load_known_attributes():
    global allowed_attributes, solver
    for fact in solver.model:
        if "ooasp_attr(" in fact:
            stripped = fact.split("(")[1][0:-2]
            class_name, attr, attr_type = stripped.split(",") 
            allowed_attributes.append({"class":class_name, "attribute":attr, "type":attr_type})
    return Response("Attributes.", data=allowed_objects)

def parse_model(m):
    """
    parses the model and only returns load-relevant facts.
    """
    res = []
    for fact in m:
        if "ooasp_isa_leaf" in fact:
            new_fact = "ooasp_isa("+fact.split("(")[1]
            res.append(new_fact)
        if "ooasp_attr_value" in fact:
            res.append(fact)
        if "ooasp_associated" in fact:
            assoc_data = fact.split("(")
            name,t1,t2 = assoc_data[-1].split(",")
            if name not in specializations.keys(): #if there does not exist a specialisation it is the leaf
                res.append(fact)
    return res

def parse_assumptions(a):
    """
    parses the model and only returns load-relevant facts.
    """
    res = []
    for fact in a:
        if "ooasp_isa" in fact:
            res.append(f"{fact}.")
        if "ooasp_attr_value" in fact:
            res.append(f"{fact}.")
        if "ooasp_associated" in fact:
            assoc_data = fact.split("(")
            name,t1,t2 = assoc_data[-1].split(",")
            if name not in specializations.keys(): #if there does not exist a specialisation it is the leaf
                res.append(f"{fact}.")
    return res

def initialise_solver(solver, data): #!
    global selected_domain
    selected_domain = os.path.split(data.domain)[0]


    object_list = data.objects.split(",") if data.objects != "" else []
    data.prio_associations = data.prio_associations.split(",")
    solver.ctl.load(data.domain)
    solver.load_base()
    solver.smart_complete()
    # check if a model with domain info was created
    if solver.model is None:
        return Response(message="Initial domain solve failed.", data=None).build()
    
    solver.initial_objects =  object_list
    solver.associations_with_priority = data.prio_associations

    solver.create_initial_objects()

    global setup_flag
    setup_flag = True

    load_known_associations()
    load_known_names()
    load_known_attributes()
    load_specializations()
    return Response(message="Solver was initialised.", data=solver.__dict__).build()

# TODO find a way to track positions

def _new_attr(node,attr):
    global solver

    found_val = None 
    for fact in solver.assumptions:
        if "ooasp_attr_value" in fact:
            val_info = fact.split("(")[-1].replace(")","")
            attr_name, target, value = val_info.split(",")
            print(fact)
            if (str(node["id"]) == str(target)) and (attr["name"] == attr_name):
                found_val = value
                break
            
    vals = set()
    vals.add(attr["value"])
    node["data"]["attributes"].append({
        "name":attr["name"],
        "values": vals,
        "active_value": found_val,
        "object_id": node["id"]
    })


    return

def export_as_file(path):
    global solver
    with open(path, "w+") as f:
        for assumption in solver.assumptions:
            f.write(f"{assumption}.\n")

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

@app.get("/save/model")
def save_model_data():
    global solver, solve_semaphore
    if not solve_semaphore:
        res =  parse_model(solver.model)
        return Response("Current model facts:", res).build()
    return Response("Solver busy.", None).build()

@app.get("/export/ooasp/{path}")
def export_to_file(path):
    export_as_file(path)
    return path

@app.post("/reset_solver")
def reset_solver():
    global solver, selected_domain
    solver = SmartOOASPSolver(smart_generation_functions=SMART_FUNCTIONS)
    print(selected_domain)
    initialise_solver(solver, InitData(objects="",prio_associations="",domain=selected_domain+"/kb.lp"))
    Response("Current Solver state.", solver.__dict__).build()

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

@app.get("/knowledgebase")
async def show_loaded_kb():
    global allowed_associations, allowed_objects, allowed_attributes
    return Response("Known class names and associations.", {"classes": allowed_objects, "associations": allowed_associations, "attributes":allowed_attributes, "specializations":specializations})


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
    new_assumptions = parse_model(solver.model)
    solver.assumptions = set()
    for fact in new_assumptions:
        solver.assumptions.add(fact[0:-1])
    solve_semaphore = False
    print("Fisnished Solving")

@app.post("/solve")
async def call_solve():
    global solve_semaphore, solver
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

@app.post("/attr_val/{name}/{target_id}/{value}")
def assign_value(name, target_id, value):
    global solver, solve_semaphore
    if solve_semaphore:
        return Response("Solver is currently busy.", data=[]).build(code=status.HTTP_503_SERVICE_UNAVAILABLE)
    solver.choose_attribute_value((str(name),target_id,value))
    return Response("Succesfully added.",data=solver.assumption_list).build(code=status.HTTP_200_OK)

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
    res_obj = []
    for item in response:
        res_obj.append({"name":item})
        
    return JSONResponse(status_code=status.HTTP_200_OK, content=res_obj)

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
    response = {"projects": [],
                "all_files": []}
    all_projects =  app.pfm.list_all_projects()
    for p in all_projects:
        metadata = app.pfm.get_project_metadata(p)
        response["projects"].append(metadata)
        for file in metadata["files"]:
            response["all_files"].append({"name":file,"project":p})

    return JSONResponse(status_code=status.HTTP_200_OK, content=response)

@app.get("/project/{project_name}")
def get_project(project_name):
    """
    Returns metadata of an existing project.
    """
    response = {"projects": app.pfm.get_project_metadata(project_name)}
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

@app.post("/request/save")
async def force_save():
    global solver, open_configuration_file, solve_semaphore
    if open_configuration_file is None:
        return Response("Cannot save. No file is opened.")
    else:
        if solve_semaphore:
            return Response("Solver is busy. State cannot be saved at this moment.")
        assumptions_copy =  copy.deepcopy(solver.assumptions)
        
        def _threaded_save():
            new_assumptions = parse_assumptions(assumptions_copy)
            with open(open_configuration_file, "w+") as f:
                for a in new_assumptions:
                    f.write(a+"\n")
            return
        t1 = threading.Thread(target=_threaded_save)
        t1.start()
    return Response("Requested a save.", assumptions_copy)

@app.get("/active_domain")
async def get_active_domain():
    global selected_domain, open_configuration_file

    return {"domain": selected_domain, "file":open_configuration_file}


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

6.) Extract attribute options
"""