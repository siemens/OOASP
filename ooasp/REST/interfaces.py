from pydantic import BaseModel
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
import os
#==========DATA MODELS========
class ProjectDataModel(BaseModel):
    domain: str|None = None
    description: str|None = None

class ProjectUpdateModel(BaseModel):
    domain: str|None = None
    description: str|None = None

class NewFile(BaseModel):
    content: str|None =""
    suffix: str|None = ".ooasp"
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

class DomainModel(BaseModel):
    name: str

class ConfigurationModel(BaseModel):
    name: str
    domain: str
    icon: str 

class DomainUpdateModel(BaseModel):
    name: str | None = None
    description: str | None = None
    kb: str | None = None
    constraints: str | None = None

class DomainDescription(BaseModel):
    description: str
