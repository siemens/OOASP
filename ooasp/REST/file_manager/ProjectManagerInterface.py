from abc import ABC, abstractmethod
import os
import os.path
import json
from pathlib import Path
from fastapi import FastAPI
import uuid

#TODO define response rules
#TODO implement renaming functionality for everything


DEFAULT_LOCATION = Path("")

SYS_FOLDER_NAME = 'interactive_configurator_files'
DOMAIN_DIR = 'domains'
CONFIG_DIR = 'configuration_files'

def make_file_structure(location):
    location = Path(location)
    os.makedirs(os.path.join(location,SYS_FOLDER_NAME), exist_ok=True)
    os.makedirs(os.path.join(location,SYS_FOLDER_NAME,DOMAIN_DIR), exist_ok=True)
    os.makedirs(os.path.join(location,SYS_FOLDER_NAME,CONFIG_DIR), exist_ok=True)
    return os.path.join(location,SYS_FOLDER_NAME)

class Domain:

    ENCODING_FNAME='kb.lp'
    CONSTRAINTS_FNAME='constraints.lp'
    METADATA='domain_conf.json'

    def __init__(self,name=None) -> None:
        self.name = name
        self.directory = None
        self.version = '0.0.0'
        self.description = None
        self.configurations = []
        self.icon = ''

    def __repr__(self):
        return str(self.__dict__)

    def _set_directory(self,alternative=None):
        if alternative is None:
            self.directory = os.path.join(DEFAULT_LOCATION,SYS_FOLDER_NAME,DOMAIN_DIR,self.name)

    def generate_new(self, content="", create_req_files=True):
        estimated_dir = os.path.join(DEFAULT_LOCATION,SYS_FOLDER_NAME,DOMAIN_DIR,self.name)

        if not os.path.exists(estimated_dir):
            print(f"New project directory will be created in '{estimated_dir}'.")
            print(f"    1. Setting domain directory to '{estimated_dir}'.")
            self.directory = estimated_dir
            os.makedirs(estimated_dir)
            if create_req_files:
                print(f"        Creating Template files: '{self.ENCODING_FNAME}','{self.CONSTRAINTS_FNAME}' ")
                with open(os.path.join(estimated_dir, self.ENCODING_FNAME),"w") as enc_file:
                    enc_file.write(f"% ===== '{self.name}' domain encoding ===== ")
                    enc_file.write(content)
                with open(os.path.join(estimated_dir, self.CONSTRAINTS_FNAME),"w") as enc_file:
                    enc_file.write(f"% ===== '{self.name}' constraint encoding ===== ")
            print("    2. Generating Domain metadata")
            metadata = {'name':self.name,
                        'directory':self.directory,
                        'version': '0.0.1',
                        'ENCODING_FNAME':self.ENCODING_FNAME,
                        'CONSTRAINTS_FNAME':self.CONSTRAINTS_FNAME,
                        'description': self.description,
                        'configurations': self.configurations,
                        'icon': self.icon
                        }
            print("    3. Writing metadata")
            with open(os.path.join(estimated_dir, self.METADATA),"w") as mf:
                json.dump(metadata,mf,indent=4)
            return True

        print(f"Project with this name ({self.name}) already exists.")
        return False

    def _check_exists(self):
        if not os.path.exists(self.directory):
            return False
        return True

    def _dump_metadata(self, other_file=None, additional_metadata={}):
        fpath = os.path.join(self.directory, self.METADATA) if other_file is None else other_file
        with open(fpath, 'w') as f:
            metadata = {'name':self.name,
                        'directory':self.directory,
                        'version': self.version,
                        'ENCODING_FNAME':self.ENCODING_FNAME,
                        'CONSTRAINTS_FNAME':self.CONSTRAINTS_FNAME,
                        'description': self.description,
                        'configurations': self.configurations,
                        'icon':self.icon
                        }
            metadata.update(additional_metadata)
            json.dump(metadata,f,indent=4)

    def _load(self, config_file, rewrite_fnames=False):
        with open(config_file, "r") as f:
            content = json.load(f)
            
            self.name = content['name']
            self.directory = content['directory']
            self.version = content['version']
            self.description = content["description"]
            self.configurations = content["configurations"]
            self.icon = content['icon']

            if rewrite_fnames:
                self.CONSTRAINTS_FNAME = content['CONSTRAINTS_FNAME']
                self.ENCODING_FNAME = content['ENCODING_FNAME']
                if self.METADATA != content['METADATA']:
                    print("    Changing metadata location, as specified in the domain config file.")
                    self._dump_metadata(os.path.join(self.directory, content['METADATA']))
                    self.METADATA = content['METADATA']
        return self
    
    def _change_description(self, description):
        self.description = str(description)
        self._dump_metadata()

    def _validate(self) -> bool:
        state = locals()
        for arg in state:
            if state[arg] is None:
                return False
        return True
    
    def _update(self, version=None, directory=None, ENCODING_FNAME=None, CONSTRAINTS_FNAME=None, METADATA=None, configurations=None, icon=None) -> dict:
        self.version = version if version is not None else self.version
        self.directory = directory if directory is not None else self.directory
        self.ENCODING_FNAME = ENCODING_FNAME if ENCODING_FNAME is not None else self.ENCODING_FNAME
        self.CONSTRAINTS_FNAME =  CONSTRAINTS_FNAME if CONSTRAINTS_FNAME is not None else self.CONSTRAINTS_FNAME
        self.METADATA = METADATA if METADATA is not None else self.METADATA
        self.configurations = configurations if configurations else self.configurations
        self.icon = icon if icon else self.icon

    def _add_configuration(self, configuration):
        new =  self.configurations
        new.append(configuration)
        self._update(CONFIGURATIONS=new)
        self._dump_metadata()
        return self

    def _delete(self):
        print(self._check_exists())
        if self._check_exists():
            try:
                os.rmdir(self.directory)
            except:
                files = os.listdir(self.directory)
                for file in files:
                    fpath = os.path.join(self.directory, file)
                    print(f"Removing domain file: '{fpath}' ")
                    os.remove(fpath)
                os.rmdir(self.directory)
        return not self._check_exists()

'''
class Project:

    METADATA = "project_conf.json"

    def __init__(self) -> None:
        self.path = None
        self.domain = None
        self.name = None
        self.description = None
        self.files = []

    def generate_new(self, name, domain, projects_path, description=None):
        self.name = name
        self.domain = domain
        self.description = description
        self.path = os.path.join(projects_path,name)

        if not os.path.exists(self.path):

            os.makedirs(self.path)
            with open(os.path.join(self.path,self.METADATA), "w") as f:
                json.dump(self.__dict__, f, indent=4)
            return self.__dict__

        print(f"Project with this name ({self.name}) already exists.")
        return {"message": f"Project with this name ({self.name}) already exists."}

    def _validate(self):
        pass
        

    def add_file(self, name, content=""):
        if name in self.files:
            return "File already exists."
        try:
            with open(os.path.join(SYS_FOLDER_NAME,CONFIG_DIR,self.name, name), "w+") as f:
                f.write(content)
                self.files.append(name)
                self._save()
                return self.files
        except:
            return "Unsuccessful. An internal error has occurred."


    def _save(self, other_file=None):
        try:
            if other_file is not None:
                with open(other_file, "w+") as f:
                    json.dump(self.__dict__, f, indent=4)
            with open(os.path.join(self.path, self.METADATA),"w") as f:
                json.dump(self.__dict__, f, indent=4)
            return True
        except:
            return False

    def _load(self, path):
        try:
            with open(path, "r+") as f:
                content = json.load(f)
                self.name = content["name"]
                self.domain = content["domain"]
                self.description = content["description"]
                self.path = content["path"]
                self.files = content["files"]
                return self
        except:
            return None

#TODO modularise this part (this is repeated in domain)-------------------------------------------------------

    def _check_exists(self):
        if not os.path.exists(self.path):
            return False
        return True

    def _delete_project(self):
        print(self._check_exists())
        if self._check_exists():
            try:
                os.rmdir(self.path)
            except:
                files = os.listdir(self.path)
                for file in files:
                    fpath = os.path.join(self.path, file)
                    print(f"Removing project file: '{fpath}' ")
                    os.remove(fpath)
                os.rmdir(self.path)
        return not self._check_exists()
    
    def _delete_file(self, fname):
        fpath = os.path.join(self.path,fname)
        if not os.path.exists(fpath):
            return False
        os.remove(fpath)
        return True
        

    def _change_description(self, desc):
        self.description = str(desc)
        self._save()
'''

class RESTManager():
    def __init__(self, domain_path, configuration_path, path) -> None:
       
        self.MAPPING_FILE =os.path.join(path,"domain-config-map.json")
        self.map_memo = None
        self.domain_path = domain_path
        self.configuration_path = configuration_path
        self.run_id = str(uuid.uuid1())
        self._load_mapping()
    
    #==========DOMAIN==========

    def _load_mapping(self):
        try:
            with open(self.MAPPING_FILE, "r+") as f:
                content = json.load(f)
                self.map_memo = content
                return True
        except:
            with open(self.MAPPING_FILE, "w+") as f:
                json.dump([],f,indent=4)
                self.map_memo = []
            return False

    def _save_mapping(self):
        with open(self.MAPPING_FILE, "w") as f:
            json.dump(self.map_memo, f, indent=4)
            return True

    def get_all_domains(self):
        return os.listdir(self.domain_path)
    
    def new_domain(self, name):
        dom = Domain(name)
        dom.generate_new()
        return str(dom.__dict__)
    
    def new_domain_with_content(self, name, content):
        dom = Domain(name)
        dom.generate_new(content=content)
        return str(dom.__dict__)
    
    def get_domain_metadata(self, name):
        available = os.listdir(self.domain_path)
        if name not in available:
            return "Domain does not exist."
        with open(os.path.join(self.domain_path, name, Domain.METADATA)) as f:
            content = json.load(f)
        return content
    
    def delete_domain(self, name):
        pass
        available = os.listdir(self.domain_path)
        #TODO find all corresponding files and orphan them
        if name not in available:
            return "Domain does not exist."
        dom = Domain()._load(str(os.path.join(DEFAULT_LOCATION,SYS_FOLDER_NAME, DOMAIN_DIR,name,Domain.METADATA)))
        if dom._delete():
            return "Domain deleted successfully."
        return "There was a problem removing the domain."
    
    def update_domain(self, name, update_data):
        def _read_metadata():
            with open(str(os.path.join(DEFAULT_LOCATION,SYS_FOLDER_NAME, DOMAIN_DIR,name,Domain.METADATA)), "r")as f:
                return str(json.load(f))

        #TODO rework this to include icons etc
        dom = Domain()._load(str(os.path.join(DEFAULT_LOCATION,SYS_FOLDER_NAME, DOMAIN_DIR,name,Domain.METADATA)))
        dom._update(version=update_data['version'], 
                    ENCODING_FNAME=update_data["ENCODING_FNAME"],
                    CONSTRAINTS_FNAME=update_data["CONSTRAINTS_FNAME"]
                    )
        dom._dump_metadata()
        return _read_metadata()

    def get_domain_description(self, name):
        with open(str(os.path.join(DEFAULT_LOCATION,SYS_FOLDER_NAME, DOMAIN_DIR,name,Domain.METADATA)), "r")as f:
                return json.load(f)["description"]

    def update_domain_description(self, name, desc):
        dom = Domain()._load(str(os.path.join(DEFAULT_LOCATION,SYS_FOLDER_NAME, DOMAIN_DIR,name,Domain.METADATA)))
        dom._change_description(desc)
        return dom.description
    
    #==========CONFIGURATIONS============
    def get_configuration_by_name(self, name):
        res = list(filter(lambda d: d["name"]== name ,self.map_memo))
        return (res[0] if len(res)> 0 else None, self.map_memo[self.map_memo.index(res[0])])
    
    def list_all_configuration_names(self):
        res = []
        for log in self.map_memo:
            res.append(log["name"])
        return res

    def new_configuration(self, name, domain, content=""):
        file_path = os.path.join(self.configuration_path, name)
        if os.path.isfile(file_path):
            return (False, "File with this name exists already.")
        known_domains = self.get_all_domains()
        if domain not in known_domains:
            return (False, "Assigned domain does not exist.")
        
        with open(file_path, "w+") as f:
            f.write(content)
        self.map_memo.append({"name": name, "domain":domain})
        self._save_mapping()
        return(True, "File created.")
    
    def rename_configuration(self, name, new_name):
        log, config = self.get_configuration_by_name(name)
        if log is None:
            return (False, "Configuration does not exist.")
        c_path = os.path.join(self.configuration_path, name)
        new_path = os.path.join(self.configuration_path, new_name)
        os.rename(c_path, new_path)

        if os.path.isfile(c_path):
            return (False, "There was a problem renaming the configuration.")
        if not os.path.isfile(new_path):
            return (False, "There was a problem renaming the configuration.")
        
        self.map_memo[self.map_memo.index(log)]["name"] = new_name
        self._save_mapping()        

    def delete_configuration(self, name):
        log, config = self.get_configuration_by_name(name)
        if log is None:
            return (False, "Configuration does not exist.")
        f_path = os.path.join(self.configuration_path, name)
        os.remove(f_path)
        if not os.path.isfile(f_path):
            self.map_memo.remove(config)
            self._save_mapping()
            return (True, "File was removed.")
        self._save_mapping()
        return (False, "There was a problem removing the file.")
        

    #==========PROJECT==========
'''
    def list_all_projects(self):
        return os.listdir(self.project_path)

    def new_project(self, name, domain, description=None):
        available_domains = os.listdir(self.domain_path)
        return Project().generate_new(name, domain, self.project_path,description)

    def new_file(self, pname, name, content, suffix=".ooasp"):
        fname = name+suffix if suffix is not None else name
        project = Project()._load(os.path.join(self.project_path,pname,Project.METADATA))
        return project.add_file(fname,content)

    def delete_project(self, name):
        available = os.listdir(self.project_path)
        if name not in available:
            return "Project does not exist."
        p = Project()._load(str(os.path.join(DEFAULT_LOCATION,SYS_FOLDER_NAME, CONFIG_DIR,name,Project.METADATA)))
        if p._delete_project():
            return "Project deleted successfully."
        return "There was a problem removing the project."

    def delete_file(self, filename, projectname):
        p = Project()._load(str(os.path.join(DEFAULT_LOCATION,SYS_FOLDER_NAME, CONFIG_DIR,projectname,Project.METADATA)))
        if p._delete_file(filename):
            return {"message": "File removed successfully."}
        return {"message": "File does not exists."}

    def list_all_files(self, name):
        #TODO check intersection of listed and real, return warnings for the ones that do not match
        project = Project()._load(os.path.join(self.project_path,name,Project.METADATA))
        if project is None:
            return {"message": "Project could not be loaded."}
        return project.__dict__

    def project_description(self, name):
        pass

    def get_project_metadata(self, name):
        project = Project()._load(os.path.join(self.project_path,name,Project.METADATA))
        if project is None:
            return {"message": "Project could not be loaded."}
        return project.__dict__

    def validate_compatibility(self, project):
        pass

    def list_files_standalone(self):
        """
        Returns a list of all known files -> how to deal with descriptions
        """
        res = list(os.walk(os.path.join(SYS_FOLDER_NAME,CONFIG_DIR)))
        return res
        
'''
        
class MyAPI(FastAPI):
    def __init__(self):
        super().__init__()
        self.pfm = RESTManager(domain_path=Path("./interactive_configurator_files/domains"),configuration_path=Path("./interactive_configurator_files/configuration_files"),path=Path("./interactive_configurator_files"))
        os.makedirs(Path("./interactive_configurator_files/domains"), exist_ok=True)
        os.makedirs(Path("./interactive_configurator_files/configuration_files"), exist_ok=True)

