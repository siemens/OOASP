# Copyright (c) 2022 Siemens AG Oesterreich
# SPDX-License-Identifier: MIT

import time
from importlib import resources
from clorm.clingo import Control
from clingo import Number, Function
from clorm import Predicate, unify
from ooasp.config import OOASPConfiguration
from ooasp.kb import OOASPKnowledgeBase
from typing import List
from copy import deepcopy
import ooasp.utils as utils
from typing import List
import ooasp.settings as settings


class State:
    """
    Represents a State in the process of an interactive configuration,
    which saves the partial configuration, the action performed  and the
    number of objects
    """
    def __init__(self, config:OOASPConfiguration,
                        action:str,
                        domain_size:int):
        """
        Creates a state
            Parameters:
                kb: The Knowledge base
                config: The partial or complete configuration
                domain_size: The number of objects in the partial configuration
                action: The action performed to get the state
        """
        self.domain_size = domain_size
        self.config = config
        self.action = action

    @classmethod
    def initial(cls, kb:OOASPKnowledgeBase, config_name:str):
        """
        Creates the initial state
            Parameters:
                kb: The Knowledge base
                config_name: The name of the configuration
        """
        return cls(OOASPConfiguration(config_name,kb),
            action="start",
            domain_size=0)

    def copy(self, action:str, deep_config:bool = False):
        """
        Creates a state by copying the state and changing some properties
            Parameters:
                action: The action for the new state
                deep_config: Whether the configuration should be copied in a deep way
        """
        if deep_config:
            config = deepcopy(self.config)
        else:
            config = self.config
        new_state = State(config,action,self.domain_size)
        return new_state

    def __str__(self)->str:
        """
        Returns a string representation of the state
        """
        info = {
        'last action' : self.action,
        'number of objects' : self.domain_size,
        'config' : str(self.config)
        }
        return utils.pretty_dic(info)


class InteractiveConfigurator:

    """
    Handles the interactive process of a configuration
        Properties:
            kb (OOASPKnowledgeBase): The Knowledge base
            config_name (str): The name of the configuration
            states (List[State]): The list of all states
            additional_files (List[str]): The list of additional lp files
            found_config (OOASPConfig):  The complete configuration found in the browsing
            brave_config (OOASPConfig):  The brave configuration found with all the options
            last_size_grounded (int): The last size that was grounded
    """

    def __init__(self, kb:OOASPKnowledgeBase, config_name:str, additional_files:List=None, additional_prg:str=""):
        """
        Creates an interactive configuratior
            Parameters:
                kb: The Knowledge base
                config_name: The name of the configuration
                additional_files: A list of .lp files to include in the control
        """
        self.kb = kb
        self.config_name = config_name
        self.states = [State.initial(kb,config_name)]
        self.additional_files = [] if additional_files is None else additional_files
        self.additional_prg = additional_prg
        self._time_grounding = 0
        self._time_solving = 0
        self._individual_ground_times = {}
        self._individual_solve_times = {}
        self._init_ctl()
        self.found_config = None
        self.brave_config = None
        self.solution_iterator = None
        self.hdn = None


    def _add_grounding_time(self, time):
        self._time_grounding+=time
        self._individual_ground_times[self.domain_size] = time

    def _add_solving_time(self, time):
        self._time_solving+=time
        self._individual_solve_times[self.domain_size] = time

    def _init_ctl(self):
        """
        Initializes the control object
        """
        self.ctl = Control(["0",
                "--warn=none",
                f"-c config_name={self.config_name}",
                f"-c kb_name={self.kb.name}"])
        self.ctl.add("base",[],self.kb.fb.asp_str())
        self.ctl.add("base",[],self.additional_prg)
        file = settings.encodings_path.joinpath("ooasp.lp")
        self.ctl.load(str(file))
        for f in self.additional_files:
            self.ctl.load(f)
        self._ground([("base",[])])
        self.last_size_grounded = 0


    def __str__(self):
        s = utils.title('INTERACTIVE CONFIG')
        d = {
            'kb' : self.kb.name,
            'config' : self.state.config.name,
            'browsing'  : self.solution_iterator is not None,
            'found configuration ' : str(self.found_config) is not None
        }
        s+= utils.pretty_dic(d)
        s+= utils.subtitle('Current State')
        s+= str(self.state)

        return s

    @property
    def state(self):
        """
        The current state of the interactive process
        """
        return self.states[-1]

    @property
    def config(self):
        """
        The current (partial) configuration being constructed
        """
        return self.state.config

    @property
    def domain_size(self):
        """
        The size of the domain (How many objects have been created)
        """
        return self.state.domain_size

    @property
    def browsing(self):
        """
        If there is a current browsing process through the solutuions
        """
        return self.solution_iterator is not None

    @property
    def history(self)->str:
        """
        A string with the history of all executed actions
        """
        h = "\n".join([f"{i}. {s.action}" for i, s in enumerate(self.states)])
        return h

    @property
    def _statistics(self):
        self._outdate_models()
        d ={
            'time-grounding' : self._time_grounding,
            'time-solving' : self._time_solving,
            'per-domain-grounding':self._individual_ground_times,
            'per-domain-solving':self._individual_solve_times
            }

        return d

    def _ground(self, args):
        start = time.time()
        self.ctl.ground(args)
        end = time.time()
        self._add_grounding_time(end -start)


    def _ground_missing(self)->None:
        """
        Grounds all missing programs based on the current domain_size
        """
        if self.domain_size == self.last_size_grounded:
            return
        domains = self.config.domains_from(self.last_size_grounded)
        for cls, s in domains:
            if s>1:
                self.ctl.release_external(Function("active", [Number(s-1)]))
            self._ground([("domain",[Number(s),Function(cls, [])])])

            self.ctl.assign_external(Function("active", [Number(s)]), True)
        self.last_size_grounded=s

    def _new_state(self,action:str,deep=False)->State:
        """
        Creates a new state
            Parameters:
                action: The action string
                deep: If the config should be deep copyed
        """
        next_state = self.state.copy(action, deep_config=deep)
        self.states.append(next_state)
        self._outdate_models()
        return next_state

    def _outdate_models(self)->None:
        """
        Outdates all models. This will cancel any browsing process and remove
        any previously computed options in the brave config
        """
        self.brave_config=None
        self.cautious_config=None
        self.found_config=None
        if self.solution_iterator:
            self.hdn.cancel()
        self.solution_iterator = None

    def _set_user_externals(self)->None:
        """
        Sets all partial configuration as user externals to True.
        This uses special predicate `user/1`
        """
        for f in self.config.editable_facts:
            # self.ctl.assign_external(Function("random",[]), True)
            self.ctl.assign_external(Function("user",[f.symbol]), True)

    def _falsify_user_externals(self,facts:List)->None:
        """
        Makes user externals false for the given facts. This is needed when a
        remove action is performed.
            Parameters:
                facts: List of clorm predicates to be set to false
        """
        for f in facts:
            self.ctl.assign_external(Function("user",[f.symbol]), False)

    def _add_fact(self, fact:Predicate)->None:
        """
        Adds a new fact to the control. The fact is added as part
        of the program for the current domain size.
            Parameters:
                fact: The clorm predicate to be added to the control
        """
        self.ctl.add("domain",[str(self.domain_size)],str(fact)+".")

    def _create_required_objects(self, cls:str, object_id:int, ignore_assoc:List=None)->None:
        """
        Creates required objects for a given object based on associations in the knowledge base configuration.
        It ensures that the minimum required number of associated objects is met for each association.
        
            Parameters:
                cls (str): The class (object type) for which required objects are being created.
                object_id (int): The ID of the object for which required objects are being created.
                ignore_assoc (List, optional): A list of association names to be ignored during object creation.
                    Defaults to None.
        """
        if ignore_assoc is None:
            ignore_assoc = set()
        assocs = self.config.kb.associations(cls)
        assocs_added = []
        for name, class2, min, max in assocs:
            # print(f"ASS: {name}")
            if name in ignore_assoc:
                continue
            curret_assoc = self.config.associated_by(object_id,name)
            remaining = min - len(curret_assoc) 
            assocs_added.append(name)
            if remaining<0:
                continue
            for _ in range(remaining):
                self._extend_domain(class2,True,assocs_added)



    def _extend_domain(self, cls='object',propagate=False, ignore_assoc:List=None)->int:
        """
        Increases the domain size by one and adds a new domain(object,N) fact to
        the configuration.
        """
        self.state.domain_size+=1
        self._outdate_models()
        new_object = self.state.domain_size
        self.config.add_domain(cls,new_object)
        if propagate:
            self._create_required_objects(cls, new_object,ignore_assoc)
        return new_object



    # --------- Browsing

    def _next_solution(self)->OOASPConfiguration:
        """
        Gets the next available solution for the current configuration without increasing the domain size.
        If there is an ongoing browsing process it will continue using
        the given iterator, otherwise it will ground any missing steps and solve.
        Sets the found configuration based on the next computed model.
            Returns:
                The found OOASPConfiguration or None if no solution is found
        """
        self._ground_missing()

        if not self.browsing:
            self.ctl.assign_external(Function("guess") , True)
            self.ctl.assign_external(Function("check_permanent_cv"), True)
            self.ctl.assign_external(Function("check_potential_cv"), True)
            self._set_user_externals()
            self.ctl.configuration.solve.enum_mode = 'auto'
            start = time.time()
            self.hdn = self.ctl.solve(yield_=True)
            end = time.time()
            self._add_solving_time(end -start)

            self.solution_iterator = iter(self.hdn)

        start = time.time()
        try:
            model = next(self.solution_iterator)
            end = time.time()
            self._add_solving_time(end -start)
            found_config = OOASPConfiguration.from_model(self.state.config.name,
                    self.kb, model)
            return found_config
        except StopIteration:
            end = time.time()
            self._add_solving_time(end -start)
            self.hdn.cancel()
            self.found_config=False
            return False

    def _set_config(self,config:OOASPConfiguration):
        """
        Sets the current configuration to the given one
            Parameters:
                config: The new configuration
            Throws:
                Error in case the size of the new configuration is smaller
        """
        new_size = config.domain_size

        if new_size < self.domain_size:
            raise RuntimeError("Can't set a configuration with smaller domain size")
        self.state.domain_size = new_size
        self.state.config=config


    def _add_objects_to_dict(self, config: OOASPConfiguration, options: dict) -> dict:
        """
        Adds the objects from the brave configuration to the provided dictionary

            Parameters:
                config: The current brave configuration
                options:The dictionary to be updated with the objects from the config
            Returns:
                The updated dictionary, now containing the objects from the configuration
        """
        user_strs = [str(s) for s in config.user_input]

        for f in config.unique_objects:
            options[f.object_id].append(utils.editable_fact_as_remove_action(f,config.UNIFIERS))
        for f in config.small_objects:
            if str(f) not in user_strs:
                options[f.object_id].append(utils.editable_fact_as_select_action(f,config.UNIFIERS))
        return options
    

    def _add_attributes_to_dict(self, config: OOASPConfiguration, options: dict) -> dict:
        """
        Adds the attributes from the brave configuration to the provided dictionary

            Parameters:
                config: The current brave configuration
                options:The dictionary to be updated with the attributes from the config
            Returns:
                The updated dictionary, now containing the attributes from the configuration
        """
        user_strs = [str(s) for s in config.user_input]
        user_fb = unify(config.editable_unifiers, config.user_input)

        for f in user_fb.query(config.UNIFIERS.AttributeValue).all():
            options[f.object_id].append(utils.editable_fact_as_remove_action(f,config.UNIFIERS))
        for f in config.fb.query(config.UNIFIERS.AttributeValue).all():
            if str(f) not in user_strs:
                options[f.object_id].append(utils.editable_fact_as_select_action(f,config.UNIFIERS))
        return options
    

    def _add_associations_to_dict(self, config: OOASPConfiguration, options: dict) -> dict:
        """
        Adds the associations from the brave configuration to the provided dictionary

            Parameters:
                config: The current brave configuration
                options:The dictionary to be updated with the associations from the config
            Returns:
                The updated dictionary, now containing the associations from the configuration
        """
        user_strs = [str(s) for s in config.user_input]
        user_fb = unify(config.editable_unifiers, config.user_input)

        for f in user_fb.query(config.UNIFIERS.Association).all():
            options[f.object_id1].append(utils.editable_fact_as_remove_action(f,self.brave_config.UNIFIERS))
            options[f.object_id2].append(utils.editable_fact_as_remove_action(f,self.brave_config.UNIFIERS))      
        for f in config.fb.query(config.UNIFIERS.Association).all():
            if str(f) not in user_strs:
                options[f.object_id1].append(utils.editable_fact_as_select_action(f,self.brave_config.UNIFIERS))
                options[f.object_id2].append(utils.editable_fact_as_select_action(f,self.brave_config.UNIFIERS))
        return options


    def _brave_config_as_options(self) -> dict:
        """
        Returns the brave configuration computed as a dictionary with
        the options per object
            Returns:
                The dictionary with ids of objects as keys and list of dicionaries as value
                representing the possible options
        """
        if self.brave_config is None:
            raise RuntimeError("A brave configuration must be computed to get it as options")
        config = self.brave_config
        options = {}
        for i in range(1,config.domain_size+1):
            options[i]=[]

        options = self._add_objects_to_dict(config, options)
        options = self._add_attributes_to_dict(config, options)
        options = self._add_associations_to_dict(config, options)

        return options


    def _get_options(self)->OOASPConfiguration:
        """
        Returns a Configuration where the facts are the union of all stable models
            Returns:
                An OOASPConfiguration object with all the options
        """

        if self.browsing:
            raise RuntimeError("Cant get options while browsing")
        self._ground_missing()
        self.ctl.assign_external(Function("guess"), True)
        self.ctl.assign_external(Function("check_permanent_cv"), True)
        self.ctl.assign_external(Function("check_potential_cv"), False)
        self._set_user_externals()
        self.ctl.configuration.solve.enum_mode = 'brave'
        with  self.ctl.solve(yield_=True) as hdn:
            brave_model = None
            for model in hdn:
                brave_model = model
            if brave_model is None:
                self.brave_config = None
                raise RuntimeError("No available options for conflicting configuration")
            self.brave_config = OOASPConfiguration.from_model(self.state.config.name,
                    self.kb, brave_model)
        return self.brave_config

    def _check(self)->bool:
        """
        Runs the checks on the current (partial) configuration.
        The generated cv atoms are added to the current configuration.
            Returns:
                True if the current (partial) configuration as no erros, False otherwise
        """
        self._ground_missing()
        self.ctl.assign_external(Function("guess"), False)
        self.ctl.assign_external(Function("check_permanent_cv"), False)
        self.ctl.assign_external(Function("check_potential_cv"), False)
        self._set_user_externals()
        self.ctl.configuration.solve.enum_mode = 'auto'
        with  self.ctl.solve(yield_=True) as hdn:
            sat = False
            for model in hdn:
                sat = True
                self.state.config = OOASPConfiguration.from_model(self.state.config.name,
                    self.kb, model)
                self.config.remove_user()
            if not sat:
                raise RuntimeError("Got UNSAT while checking for cvs")

        return not self.config.has_cv

    def _get_cautious(self)->OOASPConfiguration:
        if self.browsing:
            raise RuntimeError("Cant get cautious while browsing")
        self._ground_missing()
        self.ctl.assign_external(Function("guess"), True)
        self.ctl.assign_external(Function("check_permanent_cv"), True)
        self.ctl.assign_external(Function("check_potential_cv"), False)
        self._set_user_externals()
        self.ctl.configuration.solve.enum_mode = 'cautious'
        self.ctl.configuration.solve.opt_mode = 'optN'
        with  self.ctl.solve(yield_=True) as hdn:
            cautious_model = None
            for model in hdn:
                cautious_model = model
            if cautious_model is None:
                self.cautious_config = None
                raise RuntimeError("No available options for conflicting configuration")
            self.cautious_config = OOASPConfiguration.from_model(self.state.config.name,
                    self.kb, cautious_model)
        return self.cautious_config
    

    def _remove_association(self,assoc_name:str,object_id1:int,object_id2:int)->None:
        """
        Removes an association from the configuration
            Parameters:
                assoc_name: Name of the association
                object_id1: Id of the first object
                object_id1: Id of the second object
        """
        fact = self.config.remove_association(assoc_name,object_id1,object_id2)
        self._falsify_user_externals(fact)

    def _remove_value(self,object_id:id,attr_name:str)->None:
        """
        Removes the value of an attribute for an object
            Parameters:
                object_id: Id of the object
                attr_name: Name of the attribute
        """
        removed_facts = self.config.remove_value(object_id,attr_name)
        self._falsify_user_externals(removed_facts)

    def _remove_object(self,object_id:id)->None:
        """
        Removes the object class selection for an object
            Parameters:
                object_id: Id of the object
        """
        removed_facts = self.config.remove_object(object_id)
        self._falsify_user_externals(removed_facts)


    #------------- Available functionality

    def check(self)->None:
        """
        Creates a new state.
        Runs the checks on the current (partial) configuration.
        The generated cv atoms are added to the current configuration.
            Returns:
                True if the current (partial) configuration as no erros, False otherwise
        """
        self._new_state("Check current configuration")
        return self._check()

    def get_options(self)->None:
        """
        Creates a new state.
        Gets a Configuration where the facts are the union of all stable models.
            Returns:
                An OOASPConfiguration object with all the options
        """
        found_config = self.found_config
        self._new_state("Obtaining options")
        self.found_config=found_config
        return self._get_options()

    def next_solution(self)->OOASPConfiguration:
        """
        Creates a new state.
        Gets the next avaliable solution for the current configuration without increasing the domain size.
        If there is an ongoing browsing process it will continue using
        the given iterator, otherwise it will ground any missing steps and solve.
        Sets the found configuration based on the next computed model.
        The found configuration can be selected as the new one using select_found_configuration
            Returns:
                The found OOASPConfiguration or None if no more solutions are found
        """
        if not self.browsing:
            self._new_state("Browse solutions")
        self.found_config = self._next_solution()
        if not self.found_config:
            return None
        return self.found_config

    def end_browsing(self)->None:
        """
        Cancels any browsing process and removes
        any previously computed options in the brave config
        """
        self._outdate_models()
        return None


    # Actions changing the configuration

    def remove_association(self,assoc_name:str,object_id1:int,object_id2:int)->None:
        """
        Creates a state with a new configuration.
        Removes an association from the configuration
            Parameters:
                assoc_name: Name of the association
                object_id1: Id of the first object
                object_id1: Id of the second object
        """
        self._new_state(f"Removed association {object_id1}-{object_id2} via {assoc_name}",deep=True)
        self._remove_association(assoc_name,object_id1,object_id2)

    def remove_value(self,object_id:int,attr_name:str)->None:
        """
        Creates a state with a new configuration.
        Removes the value of an attribute for an object
            Parameters:
                object_id: Id of the object
                attr_name: Name of the attribute
        """
        self._new_state(f"Removed value for {object_id}.{attr_name}",deep=True)
        self._remove_value(object_id,attr_name)

    def remove_object_class(self,object_id:int)->None:
        """
        Creates a state with a new configuration.
        Removes the object class selection for an object
            Parameters:
                object_id: Id of the object
        """
        self._new_state(f"Removed object class for {object_id}",deep=True)
        self._remove_object(object_id)

    def select_association(self,assoc_name:str,object_id1:int,object_id2:int)->None:
        """
        Creates a state with a new configuration.
        Selects an association
            Parameters:
                assoc_name: Name of the association
                object_id1: Id of the first object
                object_id1: Id of the second object
        """
        self._new_state(f"Associated {object_id1}-{object_id2} via {assoc_name}",deep=True)
        self.config.add_association(assoc_name,object_id1,object_id2)

    def select_value(self,object_id:int,attr_name:str,attr_value)->None:
        """
        Creates a state with a new configuration.
        Removes any current selection for the attribute.
        Selects the value the attribute.
            Parameters:
                object_id: Id of the object
                attr_name: Name of the attribute
                attr_value: Value of the attribute
        """
        self._new_state(f"Set {object_id}.{attr_name}={attr_value}",deep=True)
        self._remove_value(attr_name,object_id)
        self.config.add_value(object_id,attr_name,attr_value)

    def select_object_class(self,object_id:int,object_class:str)->None:
        """
        Creates a state with a new configuration.
        Removes any current object selection for the object.
        Selects the object class for the object.
            Parameters:
                object_id: Id of the object
            Throws:
                Error in case the object_class is not really a object class
        """
        self._new_state(f"Set {object_id} of class {object_class}",deep=True)
        self._remove_object(object_id)
        try:
            self.config.add_object(object_id,object_class)
        except Exception as e:
            self.states.pop()
            raise e


    def extend_domain(self,num:int=1,cls='object',propagate=False)->None:
        """
        Creates a state with a new configuration.
        Increases the domain size and adds a new domain(object,N) fact to
        the configuration.
            Parameters:
                num: The number of new objects that will be added
        """
        self._new_state(f"Extended domain by {num} ",deep=True)
        next_num_objects = self.state.domain_size + num
        for i in range(self.state.domain_size+1,next_num_objects+1):
            self._extend_domain(cls=cls,propagate=propagate)

    def new_object(self,object_class:str)->None:
        """
        Creates a state with a new configuration.
        Increases the domain size by one and adds a new domain(object,N) fact to
        Selects the object class for the new object
        the configuration.
            Parameters:
                object_class: The name of the object class
        """
        self._new_state(f"Added object class {object_class}",deep=True)
        new_object = self._extend_domain(cls=object_class)
        try:
            self.config.add_object(new_object,object_class)
            return new_object
        except Exception as e:
            self.states.pop()
            raise e

    def extend_incrementally(self, domain_limit:int=100, overshoot:bool=False)->OOASPConfiguration:
        """
        Creates a state with a new configuration.
        Trys to find a solution for the current domain size, if a solution is
        found it is returned otherwise it will increase the domain by one
        and look for solution until one is found.
        Sets the found configuration based on the next computed model.
        The found configuration can be selected as the new one using select_found_configuration

        This will affect the Number of object in the current configuration
        even if the found configuration is never selected.

            Parameters:
                domain_limit: The limit size the domain can reach
                overshoot: If this is passed, then the required elements will be created for each object
            Returns:
                The found OOASPConfiguration or None if no more solutions are found
        """
        name = "Extend incrementally" if not overshoot else "Extend incrementally overshooting"
        self._new_state(name,deep=True)
        if overshoot:
            objs = self.config.smart_objects
            for o in objs:
                self._create_required_objects(o.class_name, o.object_id)
        self.found_config = self._next_solution()

        while not self.found_config  or self.domain_size>domain_limit:
            self._extend_domain()
            self.found_config = self._next_solution()


        if not self.found_config:
            raise RuntimeError(f"No configuration found in the domain limit {domain_limit}")

        return self.found_config

    def select_found_configuration(self)->None:
        """
        Selects the configuration found while browsing as the partial configuration.
        This way the condiguration found can be eddited or extended.
        """
        current_found_config = self.found_config
        if not current_found_config:
            print("No configuration found")
            return
        current_found_config.remove_user()
        self.set_configuration(current_found_config)
        return None

    def set_configuration(self,config:OOASPConfiguration):
        """
        Sets the current configuration to a new one
            Parameters:
                config: The new configuration
            Throws:
                Exception if the domain size of the new configuration
                is smaller.
        """
        self._new_state("Set partial configuration")
        self._set_config(config)

    #------------- Visualize

    def view_kb(self)->None:
        """
        Shows the image of the KB in a jupyter notebook
        """
        self.kb.save_png()
        from IPython.display import Image
        return Image(f"out/{self.kb.name}.png")

    def view(self)->None:
        """
        Shows the image of the configuration in a jupyter notebook
        """
        return self.state.config.view()

    def view_found(self)->None:
        """
        Shows the image of the found configuration in a jupyter notebook
        """
        if not self.found_config:
            raise RuntimeError("No compleate configuration found")
        return self.found_config.view()


    def show_options(self)->None:
        """
        Prints the options for the current configuration.
        A brave config is computed with get_options it it was not computed already
        """
        if self.brave_config is None:
            self.get_options()
        opts = self._brave_config_as_options()
        print("")
        for k,v in opts.items():
            print(utils.subtitle(f"Options for object {k}",'PURPLE'))
            print("\n".join([e['str'] for e in v]))

    def show_history(self)->None:
        """
        Prints the hisotry
        """
        print(self.history)
