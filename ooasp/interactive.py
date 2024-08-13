# Copyright (c) 2022 Siemens AG Oesterreich
# SPDX-License-Identifier: MIT

import time
from importlib import resources
from clorm.clingo import Control
from clingo import Number, Function
from clingo.ast import ProgramBuilder, parse_files
from clorm import Predicate, unify
from ooasp.config import OOASPConfiguration
from ooasp.kb import OOASPKnowledgeBase
from typing import List
from copy import deepcopy
import ooasp.utils as utils
from typing import List
import ooasp.settings as settings
from clingcon import ClingconTheory
from fclingo import THEORY, Translator
from fclingo.__main__ import CSP
from fclingo.parsing import HeadBodyTransformer
from fclingo.translator import ConstraintAtom


def log(x):
    """
    Logs some given input in string format
    Can be activated or deactivated for debugging
    """
    pass

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


DEF = "__def"

class FclingoConfig:
    """
    Class for application specific options.
    """

    def __init__(self, min_int, max_int, print_translation, print_auxiliary):
        self.print_aux = print_auxiliary
        self.print_trans = print_translation
        self.min_int = min_int
        self.max_int = max_int
        self.defined = DEF

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
            cautious_config (OOASPConfig):  The cautious configuration found with all the inferences
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
        self.theory = ClingconTheory()
        self._init_ctl()
        self.found_config = None
        self.brave_config = None
        self.cautious_config = None
        self.solution_iterator = None
        self.hdn = None


    def _add_grounding_time(self, time:int):
        """
        Adds time to grounding for benchmarks
        Parameters:
            time (int): time to add
        """
        self._time_grounding+=time
        self._individual_ground_times[self.domain_size] = time

    def _add_solving_time(self, time):
        """
        Adds time to solving for benchamrks
        Parameters:
            time (int): time to add
        """
        self._time_solving+=time
        if not self.domain_size in self._individual_solve_times:
            self._individual_solve_times[self.domain_size] = 0

        self._individual_solve_times[self.domain_size] += time

    def _init_ctl(self):
        """
        Initializes the control object
        """
        self.ctl = Control(["0",
                "--warn=none",
                f"-c config_name={self.config_name}",
                f"-c kb_name={self.kb.name}"])
        self.theory.register(self.ctl)
        self.ftranslator = Translator(self.ctl, FclingoConfig(0, 1000, False, False))
        self.ctl.add("base", [], THEORY)
        self.ctl.add("base",[],self.kb.fb.asp_str())
        self.ctl.add("base",[],self.additional_prg)
        files = [str(settings.encodings_path.joinpath("ooasp.lp"))] + self.additional_files
        with ProgramBuilder(self.ctl) as pb:
            hbt = HeadBodyTransformer()
            parse_files(
                files,
                lambda ast: self.theory.rewrite_ast(ast, lambda stm: pb.add(hbt.visit(stm))),
            )
        self._ground([("base",[])])
        self.last_size_grounded = 0


    def __str__(self):
        """
        String representation
        """
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

    def theory_on_model(self, model) -> None:
        model = model.model_
        defined =  [s.arguments[0] for s in model.symbols(shown=True) if str(s).startswith("__def")]
        for key, val in self.theory.assignment(model.thread_id):
            if key in defined:
                f = Function("ooasp_attr_value", key.arguments+[Number(int(str(val)))])
                model.extend([f])

    @property
    def state(self) -> State:
        """
        The current state of the interactive process
        """
        return self.states[-1]

    @property
    def config(self) -> OOASPConfiguration:
        """
        The current (partial) configuration being constructed
        """
        return self.state.config

    @property
    def domain_size(self) -> int:
        """
        The size of the domain (How many objects have been created)
        """
        return self.state.domain_size

    @property
    def browsing(self) -> bool:
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
        s = 0
        for cls, s in domains:
            if s>1:
                self.ctl.release_external(Function("active", [Number(s-1)]))
            self._ground([("domain",[Number(s),Function(cls, [])])])

            self.ctl.assign_external(Function("active", [Number(s)]), True)
        self.last_size_grounded=s

    def _translate_fclingo(self)->None:
        """
        Fclingo translation that needs to be done before each solve call
        """
        new_theory_atoms = set()
        for atom in self.ctl.theory_atoms:
            new_theory_atoms.add(ConstraintAtom.copy(atom))
        self.ftranslator.translate(new_theory_atoms)

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
        self.found_config=None
        self.cautious_config=None
        if self.solution_iterator:
            if not self.hdn.wait(0):
                print("Handler still not done, can't be canceled") 
                self.hdn = None
            elif self.hdn:
                self.hdn    .cancel()
        self.solution_iterator = None

    def _set_user_externals(self)->None:
        """
        Sets all partial configuration as user externals to True.
        This uses special predicate `user/1`
        """
        for f in self.config.all_as_user():
            self.ctl.assign_external(f, True)

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
    
    def _create_required_objects(self, interested_object_id:int=None)->int:
        """
        Creates all the required objects
        Parameters:
            interested_object_id: An optional object id to only add objects associated to this object

        """
        create = True
        objects_added = set()
        while(create):
            log("\n New round")
            create = False
            cautious =  self._get_cautious()
            common_violations = cautious.constraint_violations
            log(cautious)
            for cv in common_violations:
                # TODO maybe improove performance using query
                if cv.name != 'lowerbound':
                    continue
                object_id = cv.object_id
                if interested_object_id and object_id!= interested_object_id:
                    continue
                log(f"========== Object to check {object_id}")

                assoc, cmin, n, c, opt, _ = cv.args.symbol.arguments
                for _ in range(n.number,cmin.number):
                    log(f'----Adding obejct {c.name}')
                    object2 = self._new_object(c.name)
                    objects_added.add(object2)
                    log(f"Added object {object2}")
                    if str(opt) == '1':
                        self.config.add_association(assoc.name,object_id,object2)
                    else:
                        self.config.add_association(assoc.name,object2,object_id)
                create = True
                break

        return objects_added

    
    def _extend_domain(self, cls='object')->int:
        """
        Increases the domain size by one and adds a new domain(object,N) fact to
        the configuration.
        """
        self.state.domain_size+=1
        self._outdate_models()
        new_object = self.state.domain_size
        self.config.add_domain(cls,new_object)
        return new_object

    def _new_object(self, object_class, propagate=False)->int:
        """
        Increases the domain size by one and adds an object of the given class

        Parameters:
            object_class (_type_): Class of the object
            propagate (bool, optional): If it should propagate creation. Defaults to False.

        Returns:
            int: Identifier of the new object
        """
        new_object = self._extend_domain(cls=object_class)
        self.config.add_object(new_object,object_class)
        if propagate:
            self._create_required_objects(new_object)
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
        log(f"Finding solution with {self.domain_size}")
        self._ground_missing()
        if not self.browsing:
            self.ctl.assign_external(Function("guess") , True)
            self.ctl.assign_external(Function("check_permanent_cv"), True)
            self.ctl.assign_external(Function("check_potential_cv"), True)
            self._set_user_externals()
            self.ctl.configuration.solve.enum_mode = 'auto'
            self.ctl.configuration.solve.opt_mode = 'ignore'
            start = time.time()
            self._translate_fclingo()
            self.hdn = self.ctl.solve(yield_=True)
            end = time.time()
            self._add_solving_time(end -start)

            self.solution_iterator = iter(self.hdn)

        start = time.time()
        try:
            model = next(self.solution_iterator)
            self.theory_on_model(model)
            end = time.time()
            self._add_solving_time(end -start)
            found_config = OOASPConfiguration.from_model(self.config.name,
                    self.kb, model)
            return found_config
        except StopIteration:
            end = time.time()
            self._add_solving_time(end -start)
            if self.hdn:
                self.hdn.cancel()
            self.found_config=False
            return False

    def _set_config(self,config:OOASPConfiguration, set_user_facts = True):
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
        if set_user_facts:
            config.consider_as_user(config.editable_facts)



    def _add_objects_to_dict(self, config: OOASPConfiguration, options: dict) -> None:
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
    

    def _add_attributes_to_dict(self, config: OOASPConfiguration, options: dict) -> None:
        """
        Adds the attributes from the brave configuration to the provided dictionary

            Parameters:
                config: The current brave configuration
                options:The dictionary to be updated with the attributes from the config
            Returns:
                The updated dictionary, now containing the attributes from the configuration
        """
        ui = config.user_input
        user_strs = [str(s) for s in ui]

        for f in ui.query(config.UNIFIERS.AttributeValue).all():
            options[f.object_id].append(utils.editable_fact_as_remove_action(f,config.UNIFIERS))
        for f in config.attribute_values:
            if str(f) not in user_strs:
                options[f.object_id].append(utils.editable_fact_as_select_action(f,config.UNIFIERS))
    

    def _add_associations_to_dict(self, config: OOASPConfiguration, options: dict) -> None:
        """
        Adds the associations from the brave configuration to the provided dictionary

            Parameters:
                config: The current brave configuration
                options:The dictionary to be updated with the associations from the config
            Returns:
                The updated dictionary, now containing the associations from the configuration
        """
        ui = config.user_input
        user_strs = [str(s) for s in ui]

        for f in ui.query(config.UNIFIERS.Association).all():
            options[f.object_id1].append(utils.editable_fact_as_remove_action(f,self.brave_config.UNIFIERS))
            options[f.object_id2].append(utils.editable_fact_as_remove_action(f,self.brave_config.UNIFIERS))      
        for f in config.fb.query(config.UNIFIERS.Association).all():
            if str(f) not in user_strs:
                options[f.object_id1].append(utils.editable_fact_as_select_action(f,self.brave_config.UNIFIERS))
                options[f.object_id2].append(utils.editable_fact_as_select_action(f,self.brave_config.UNIFIERS))


    def _brave_config_as_options(self) -> dict:
        """
        Returns the brave configuration computed as a dictionary with
        the options per object
            Returns:
                The dictionary with ids of objects as keys and list of dicionaries as value
                representing the possible options
        """
        options = {}
        for i in range(1,self.config.domain_size+1):
            options[i]=[]

        if self.brave_config is None:
            for f in self.config.user_input:
                if f.__class__.__name__ == 'Association':
                    options[f.object_id1].append(utils.editable_fact_as_remove_action(f,self.config.UNIFIERS))
                    options[f.object_id2].append(utils.editable_fact_as_remove_action(f,self.config.UNIFIERS))
                else:
                    options[f.object_id].append(utils.editable_fact_as_remove_action(f,self.config.UNIFIERS))
            return options


        int_attributes = self.brave_config.int_attributes
        for atti in int_attributes:
            for v in range(atti.min,atti.max):
                attr_value = self.brave_config.UNIFIERS.AttributeValue(atti.attr_name,atti.object_id,Number(v))
                self.brave_config.fb.add(attr_value)
        self._add_objects_to_dict(self.brave_config, options)
        self._add_attributes_to_dict(self.brave_config, options)
        self._add_associations_to_dict(self.brave_config, options)


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
        self._translate_fclingo()
        self.ctl.configuration.solve.enum_mode = 'brave'
        self.ctl.configuration.solve.opt_mode = 'ignore'
        start = time.time()
        with  self.ctl.solve(yield_=True) as hdn:
            brave_model = None
            for model in hdn:
                brave_model = model
            if brave_model is None:
                self.brave_config = None
            else:
                self.brave_config = OOASPConfiguration.from_model(self.state.config.name,
                    self.kb, brave_model)
        end = time.time()
        self._add_solving_time(end -start)
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
        self._translate_fclingo()
        self.ctl.configuration.solve.enum_mode = 'auto'
        self.ctl.configuration.solve.opt_mode = 'ignore'
        start = time.time()
        with  self.ctl.solve(yield_=True) as hdn:
            sat = False
            for model in hdn:
                self.theory_on_model(model)
                sat = True
                checked_config = OOASPConfiguration.from_model(self.config.name,
                    self.kb, model)
                self._set_config(checked_config)
            if not sat:
                raise RuntimeError("Got UNSAT while checking for cvs")

        end = time.time()
        self._add_solving_time(end -start)
        return not self.config.has_cv

    def _get_cautious(self)->OOASPConfiguration:
        """
        Gets the cautious consequences, also incudes an optimization statement 
        to only consider the models where lowerbound violations are minimized

        Raises:
            RuntimeError: If the configuration is conflicting and has no models

        Returns:
            OOASPConfiguration: A configuration with the intersection of all optimal models.

        """
        if self.browsing:
            raise RuntimeError("Cant get cautious while browsing")
        if self.cautious_config:
            return self.cautious_config
        self._ground_missing()
        self.ctl.assign_external(Function("guess"), True)
        self.ctl.assign_external(Function("check_permanent_cv"), True)
        self.ctl.assign_external(Function("check_potential_cv"), False)
        self._set_user_externals()
        self._translate_fclingo()
        self.ctl.configuration.solve.enum_mode = 'cautious'
        self.ctl.configuration.solve.opt_mode = 'optN'
        start = time.time()
        with  self.ctl.solve(yield_=True) as hdn:
            cautious_model = None
            for model in hdn:
                cautious_model = model
            if cautious_model is None:
                self.cautious_config = None
            else: 
                self.cautious_config = OOASPConfiguration.from_model(self.state.config.name,
                    self.kb, cautious_model)
        end = time.time()
        self._add_solving_time(end -start)
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

    def add_inferences(self)->None:
        """
        Creates a new state.
        Gets a Configuration where the facts are the intersection of all stable models optimized to minimize errors.
        Sets this configuration as the current one
            Returns:
                An OOASPConfiguration object with all the forced decisions
        """
        self._new_state("Add inferences")
        cautious = self._get_cautious()
        if cautious:
            self._set_config(cautious,set_user_facts=True)
        return 
    
    def get_inferences(self)->None:
        """
        Creates a new state.
        Gets a Configuration where the facts are the intersection of all stable models optimized to minimize errors.
            Returns:
                An OOASPConfiguration object with all the forced decisions
        """
        self._new_state("Obtaining inferences")
        return self._get_cautious()
    
    def create_all_required_objects(self)->int:
        """
        Creates a new state.
        Adds all required objects to the configuration
        """
        self._new_state("Creates all required objects")
        return self._create_required_objects()
    
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

    def remove_cvs(self)->None:
        """
        Creates a state with a new configuration.
        Removes all the constraint violations
        """
        self._new_state(f"Removed constraint violations",deep=True)
        self.config.remove_cvs()

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
        self._remove_value(object_id,attr_name)
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


    def extend_domain(self,num:int=1,cls='object')->None:
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
            self._extend_domain(cls=cls)

    def new_object(self,object_class:str, propagate=False)->None:
        """
        Creates a state with a new configuration.
        Increases the domain size by one and adds a new domain(object,N) fact to
        Selects the object class for the new object
        the configuration.
            Parameters:
                object_class: The name of the object class
        """
        self._new_state(f"Added object class {object_class}",deep=True)
        try:
            return self._new_object(object_class, propagate)
        except Exception as e:
            self.states.pop()
            raise e

    def extend_incrementally(self, domain_limit:int=100, overshoot:bool=False, step_size=1)->OOASPConfiguration:
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
            self._create_required_objects()
        self.found_config = self._next_solution()

        while not self.found_config  and self.domain_size<domain_limit:
            n_objects_added = 0
            if overshoot:
                self._outdate_models()
                n_objects_added = len(self._create_required_objects())
            while n_objects_added<step_size:
                self._extend_domain()
                n_objects_added += 1
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
            return
        current_found_config.remove_user()
        self.set_configuration(current_found_config)
        return None

    def set_configuration(self,config:OOASPConfiguration, set_user_facts=True):
        """
        Sets the current configuration to a new one
            Parameters:
                config: The new configuration
            Throws:
                Exception if the domain size of the new configuration
                is smaller.
        """
        self._new_state("Set partial configuration")
        self._set_config(config, set_user_facts=set_user_facts)

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
        return self.config.view()

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
