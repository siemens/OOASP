# Copyright (c) 2022-2024 Siemens AG Oesterreich
# SPDX-License-Identifier: MIT

import os
import datetime

from typing import List, Annotated

from clingo import Control

ELEMENT_NAMES = 'ABCD'
ELEMENT_TYPES = len(ELEMENT_NAMES)

domain_sizes: Annotated[List[int], "Currently known minimal domain sizes calculated by count.py script"] = [
    19, 33, 51, 65, 84, 98, 116, 130, 149, 163, 181, 195, 214, 228, 246, 260, 279, 293, 311, 325
    ]

instances: Annotated[List[int], "Iteration identifications."] = [x+1 for x in range(20)]


def generate_ids(n: int) -> List[str]:
    """
    Generates combinations of element definitions
    with suitable IDs.
    :param n: int, number of elements of each type (e.g. for iteration 4, n=4)
    :return: list of fact representations strings 
    """

    ids = [id+1 for id in range(ELEMENT_TYPES*n)]
    assigned = [ids[i*n:i*n+n] for i in range(ELEMENT_TYPES)]
    partial_config_facts = []

    for element_index, object_ids in enumerate(assigned):
        for id in object_ids:
            partial_config_facts.append(f"user(ooasp_isa(element{ELEMENT_NAMES[element_index]},{id})).")

    return partial_config_facts


def rewrite_assumptions(content: List[str], save: bool = True) -> None:
    """
    Rewrites the assumptions.lp file to the list of content passed.
    If save is set to true, creates a legacy directory and saves a copy of existing assumptions to it.
    :param content: list of configuration facts
    :param save: if active, saves all the generated files iin the outdated instances directory 
    """

    if os.path.isfile('instances/assumptions.lp'):
        if save:
            os.makedirs('instances/outdated', exist_ok=True)
            new_file = f"instances/outdated/assumptions{len(content)}{str(datetime.datetime.now()).replace(' ', '_').replace('.', '-').replace(':', '-')}.lp"
            os.rename('instances/assumptions.lp', new_file)
    os.makedirs('instances', exist_ok=True)
    with open('instances/assumptions.lp', 'w') as file:
        print(" >>Rewriting assumptions.")
        for t in content:
            file.write(t+'\n')


def add_domain(size: int) -> None:
    """
    Adds domain size constraints to the assumption file
    :param size: size of the domain
    """
    with open('instances/assumptions.lp', 'a') as file:
        t = f'ooasp_domain(object,1..{size}).'
        file.write(t)


def build_assumptions(n: int, save: bool = False) -> None:
    """
    Builds the new assumptions file in its entirety.
    :param n: number of iteration
    :param save: flag to save old assumption files before rewriting them
    """
    partial_config_facts = generate_ids(n)
    rewrite_assumptions(partial_config_facts, save=save)
    add_domain(domain_sizes[n-1] if len(domain_sizes) >= n else 100) # 100 is a placeholder value to avoid potential errors


def reset_solving() -> Control:
    """
    Reinitialises the clingo control.
    Returns the set up instance.
    """
    ctl = Control(["--opt-mode=ignore",
                   "--warn=none"])
    ctl.load("singleshot.lp")
    ctl.ground([("base", [])])
    return ctl


def log_model(model, out: bool=False) -> None:
    """
    Creates a model directory (if it does not exist)
    And logs resulting models into files
    :param model: representation of the model
    :param out: flag to turn on stdout prints of the model
    """
    os.makedirs('results/models', exist_ok=True)

    global timestr
    new_file = f"results/models/M{iteration}{timestr}.txt"
    with open(new_file, 'w') as mfile:
        mfile.write(str(model))
        if out:
            print('MODEL:')
            print(model)


def log_results(stats: str, iteration: int, out: bool = False) -> None:
    """
    Creates a results directory (if it does not exist)
    And logs times and results into text files.
    :param stats: statistics to write into the file
    :param iteration: identificator of the iteration
    :param out: flag to activate stdout prints of the results
    """
    os.makedirs('results/times', exist_ok=True)
    global timestr
    new_file = f"results/times/R{iteration}{timestr}.txt"
    with open(new_file, 'w') as mfile:
        mfile.write(stats)
        if out:
            print('RESULTS:')
            print(stats)


def on_model(m):
    """
    Helper function to control resulting model
    """
    log_model(m)


if __name__ == "__main__":
    global timestr
    timestr = str(datetime.datetime.now()).replace(' ', '_').replace('.', '-').replace(':', '-')
    for iteration in instances:
        print(f">>Solving for:{iteration}")
        build_assumptions(iteration)
        ctl = reset_solving()
        ctl.solve(on_model=on_model)
        log_results(str(ctl.statistics['summary']['times']), iteration, out=True)
