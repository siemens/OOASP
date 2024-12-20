# Copyright (c) 2024 Siemens AG Oesterreich
# SPDX-License-Identifier: MIT

from abc import ABC, abstractmethod
import os
import os.path
import json
from pathlib import Path
from fastapi import FastAPI
import uuid
import shutil

DEFAULT_LOCATION = Path("")

SYS_FOLDER_NAME = 'interactive_configurator_files'
DOMAIN_DIR = 'domains'
CONFIG_DIR = 'configuration_files'
METADATA = 'domain_conf.json'


def make_file_structure(location):
    """
    Creates necessary file structure to accommodate the domain and configuration file management.
    """
    location = Path(location)
    os.makedirs(os.path.join(location, SYS_FOLDER_NAME), exist_ok=True)
    os.makedirs(os.path.join(location, SYS_FOLDER_NAME, DOMAIN_DIR), exist_ok=True)
    os.makedirs(os.path.join(location, SYS_FOLDER_NAME, CONFIG_DIR), exist_ok=True)
    return os.path.join(location, SYS_FOLDER_NAME)


class Domain:

    ENCODING_FNAME = 'kb.lp'
    CONSTRAINTS_FNAME = 'constraints.lp'
    METADATA = METADATA  # needs to be reassigned to be available within the object

    def __init__(self, name=None) -> None:
        self.name = name
        self.directory = None
        self.version = '0.0.0'
        self.description = None
        self.configurations = []
        self.templates = []
        self.icon = ''

    def __repr__(self):
        return str(self.__dict__)

    def _set_directory(self, alternative=None):
        if alternative is None:
            self.directory = os.path.join(DEFAULT_LOCATION, SYS_FOLDER_NAME, DOMAIN_DIR, self.name)

    def _register_template(self, name):
        """
        Lists template as part of the domain.
        """
        self.templates.append(name)
        self._dump_metadata()

    def generate_new(self, content="", create_req_files=True, additional_constraint_files=[]):
        """
        Generates a new and empty Domain and creates the required files for it to be accessible by other systems.
        """
        estimated_dir = os.path.join(DEFAULT_LOCATION, SYS_FOLDER_NAME, DOMAIN_DIR, self.name)

        if os.path.exists(estimated_dir):
            print(f"Project with this name ({self.name}) already exists.")
            return False

        print(f"New project directory will be created in '{estimated_dir}'.")
        print(f"    1. Setting domain directory to '{estimated_dir}'.")
        self.directory = estimated_dir
        os.makedirs(estimated_dir)
        os.makedirs(os.path.join(estimated_dir, "templates"))
        if create_req_files:
            print(f"        Creating Template files: '{self.ENCODING_FNAME}','{self.CONSTRAINTS_FNAME}' ")
            with open(os.path.join(estimated_dir, self.ENCODING_FNAME), "w") as enc_file:
                enc_file.write(f"% ===== '{self.name}' domain encoding ===== ")
                enc_file.write(content)
            with open(os.path.join(estimated_dir, self.CONSTRAINTS_FNAME), "w") as enc_file:
                enc_file.write(f"% ===== '{self.name}' constraint encoding ===== ")
        print("    2. Generating Domain metadata")
        metadata = {'name': self.name,
                    'directory': self.directory,
                    'version': '0.0.1',
                    'ENCODING_FNAME': self.ENCODING_FNAME,
                    'CONSTRAINTS_FNAME': [self.CONSTRAINTS_FNAME]+additional_constraint_files,
                    'description': self.description,
                    'configurations': self.configurations,
                    'templates': self.templates,
                    'icon': self.icon
                    }
        print("    3. Writing metadata")
        with open(os.path.join(estimated_dir, self.METADATA), "w") as mf:
            json.dump(metadata, mf, indent=4)
        return True

    def _check_exists(self):
        if not os.path.exists(self.directory):
            return False
        return True

    def _dump_metadata(self, other_file=None, additional_metadata={}):
        """
        Saves metadata into physical memory.
        """
        fpath = os.path.join(self.directory, self.METADATA) if other_file is None else other_file
        with open(fpath, 'w') as f:
            metadata = self.__dict__
            metadata.update(additional_metadata)
            json.dump(metadata, f, indent=4)

    def _load(self, config_file, rewrite_fnames=False):
        """
        Loads the data from physical memory and sets all values accordingly in the object.
        """
        with open(config_file, "r") as f:
            content = json.load(f)

            self.name = content['name']
            self.directory = content['directory']
            self.version = content['version']
            self.description = content["description"]
            self.configurations = content["configurations"]
            self.templates = content['templates']
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
        """
        Updates provided attributes.
        """
        self.version = version if version is not None else self.version
        self.directory = directory if directory is not None else self.directory
        self.ENCODING_FNAME = ENCODING_FNAME if ENCODING_FNAME is not None else self.ENCODING_FNAME
        self.CONSTRAINTS_FNAME = CONSTRAINTS_FNAME if CONSTRAINTS_FNAME is not None else self.CONSTRAINTS_FNAME
        self.METADATA = METADATA if METADATA is not None else self.METADATA
        self.configurations = configurations if configurations else self.configurations
        self.icon = icon if icon else self.icon

    def _update_kb_content(self, content):
        with open(os.path.join(self.directory, self.ENCODING_FNAME), "w+") as f:
            f.write(content)

    def _update_constraint_content(self, content):
        with open(os.path.join(self.directory, self.CONSTRAINTS_FNAME), "w+") as f:
            f.write(content)

    def _update_name(self, name, new_path):
        """
        Changes name of the domain
        """
        try:
            os.rename(self.directory, new_path)
            self.name = name
            self.directory = new_path
        except:
            pass

    def _add_configuration(self, configuration):
        """
        Lists a configuration file as a part of the domain.
        """
        new = self.configurations
        new.append(configuration)
        self._update(CONFIGURATIONS=new)
        self._dump_metadata()
        return self

    def _delete(self):
        """
        Removes the domain.
        Attempts to remove all files within the Domain directory, then deletes the directory.
        """
        print(self._check_exists())
        if self._check_exists():
            try:
                os.rmdir(self.directory)
            except:
                for template in os.listdir(os.path.join(self.directory, "templates")):
                    fpath = os.path.join(self.directory, "templates", template)
                    os.remove(fpath)
                    print(f"Removing domain file: '{fpath}' ")
                os.rmdir(os.path.join(self.directory, "templates"))

                files = os.listdir(self.directory)
                for file in files:
                    fpath = os.path.join(self.directory, file)
                    print(f"Removing domain file: '{fpath}' ")
                    os.remove(fpath)
                os.rmdir(self.directory)

        return not self._check_exists()


class RESTManager():
    def __init__(self, domain_path, configuration_path, path) -> None:

        self.MAPPING_FILE = os.path.join(path, "domain-config-map.json")
        self.map_memo = None
        self.domain_path = domain_path
        self.configuration_path = configuration_path
        self.run_id = str(uuid.uuid1())
        self._load_mapping()

    # ==========DOMAIN==========

    def add_template_to_domain(self, name, template):
        """
        Registers a template as a part of the corresponding domain.
        """
        if not os.path.isfile(os.path.join(self.domain_path, name, "templates", template)):
            return False
        dom = Domain()._load(os.path.join(self.domain_path, name, METADATA))
        dom._register_template(template)
        return True

    def get_domain_templates(self, name):
        """
        Returns list of all templates registered within requested domain.
        """
        dom = Domain()._load(os.path.join(self.domain_path, name, METADATA))
        return dom.templates

    def get_full_domain_response(self):
        """
        Builds a complete JSON representation of domains and configurations recognized by the system.
        """
        res = []
        domains = self.get_all_domains()
        for domain_name in domains:
            try:
                domain = Domain(domain_name)._load(os.path.join(self.domain_path, domain_name, METADATA))
                obj = {"name": domain_name,
                       "description": domain.description,
                       "icon": domain.icon,
                       "configurations": list(filter(lambda d: d["domain"] == domain_name, self.map_memo))
                       }
                res.append(obj)
            except:
                continue
        return res

    def _load_mapping(self): 
        """
        Loads contents of configuration mapping file into the instance from physical memory.
        """
        try:
            with open(self.MAPPING_FILE, "r+") as f:
                content = json.load(f)
                self.map_memo = content
                return True
        except:
            with open(self.MAPPING_FILE, "w+") as f:
                json.dump([], f, indent=4)
                self.map_memo = []
            return False

    def _save_mapping(self):
        """
        Saves current state of the configuration mapping into physical memory.
        """
        with open(self.MAPPING_FILE, "w") as f:
            json.dump(self.map_memo, f, indent=4)
            return True

    def get_all_domains(self):
        """
        Returns list of all directories within the loaded domain directory.
        """
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
        """
        Deletes a corresponding domain.
        """
        available = os.listdir(self.domain_path)
        if name not in available:
            return "Domain does not exist."
        dom = Domain()._load(str(os.path.join(DEFAULT_LOCATION, SYS_FOLDER_NAME, DOMAIN_DIR, name, Domain.METADATA)))
        if dom._delete():
            for conf in self.map_memo:
                if conf["domain"] == name:
                    conf["domain"] == None
            self._save_mapping()
            return "Domain deleted successfully."
        return "There was a problem removing the domain."

    def update_domain(self, name, new_name, description, constraintsFiles, encodingFile):
        """
        Updates information about domain, including contents of the encoding files.
        """
        dom = Domain()._load(str(os.path.join(DEFAULT_LOCATION, SYS_FOLDER_NAME, DOMAIN_DIR, name, Domain.METADATA)))
        if description is not None:
            dom._change_description(description)

        if constraintsFiles is not None or constraintsFiles != []:
            print(constraintsFiles)
            for f in constraintsFiles:
                additional_file_path = os.path.join(self.domain_path, name, f.filename)
                with open(additional_file_path, "wb") as buffer:
                    shutil.copyfileobj(f.file, buffer)

        if encodingFile is not None:
            with open(os.path.join(self.domain_path, name, dom.ENCODING_FNAME), "wb") as buffer:
                shutil.copyfileobj(encodingFile.file, buffer)
        dom._dump_metadata()
        if new_name is not None:
            dom._update_name(new_name, os.path.join(self.domain_path, new_name))
        dom._dump_metadata()
        dom.directory = str(dom.directory)
        return dom.__dict__

    def get_domain_description(self, name):
        with open(str(os.path.join(DEFAULT_LOCATION, SYS_FOLDER_NAME, DOMAIN_DIR, name, Domain.METADATA)), "r")as f:
            return json.load(f)["description"]

    def update_domain_description(self, name, desc):
        dom = Domain()._load(str(os.path.join(DEFAULT_LOCATION, SYS_FOLDER_NAME, DOMAIN_DIR, name, Domain.METADATA)))
        dom._change_description(desc)
        return dom.description

    # ==========CONFIGURATIONS============
    def get_configuration_by_name(self, name):
        """
        Returns all data for a corresponding domain if it exists within the known mapping.
        """
        res = list(filter(lambda d: d["name"] == name, self.map_memo))
        print(res, name)
        return (res[0] if len(res) > 0 else None, self.map_memo[self.map_memo.index(res[0])])

    def list_all_configuration_names(self):
        res = []
        for log in self.map_memo:
            res.append(log["name"])
        return res

    def new_configuration(self, name, domain, description, icon="bi bi-bezier2", content=""):
        """
        Creates a new configuration and fills required data by default values if not provided.
        """
        if (icon == "") or (icon is None):
            icon = "bi bi-bezier2"
        file_path = os.path.join(self.configuration_path, name)
        if os.path.isfile(file_path):
            return (False, "File with this name exists already.")
        known_domains = self.get_all_domains()
        if domain not in known_domains:
            return (False, "Assigned domain does not exist.")

        with open(file_path, "w+") as f:
            f.write(content)
        self.map_memo.append({"name": name, "domain": domain, "icon": icon, "description": description})
        self._save_mapping()
        return (True, {"name": name, "domain": domain, "icon": icon, "description": description})

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
        return (True, self.map_memo)

    def change_icon(self, name, icon):
        log, config = self.get_configuration_by_name(name)
        if log is None:
            return (False, "Configuration does not exist.")

        self.map_memo[self.map_memo.index(log)]["icon"] = icon
        self._save_mapping()
        return (True, self.map_memo)

    def change_configuration_description(self, name, desc):
        log, config = self.get_configuration_by_name(name)
        if log is None:
            return (False, "Configuration does not exist.")
        self.map_memo[self.map_memo.index(log)].update({"description": desc})
        self._save_mapping()
        return (True, self.map_memo)

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


class MyAPI(FastAPI):
    def __init__(self):
        super().__init__()
        make_file_structure(".")
        self.pfm = RESTManager(domain_path=Path("./interactive_configurator_files/domains"), configuration_path=Path(
            "./interactive_configurator_files/configuration_files"), path=Path("./interactive_configurator_files"))
