# Copyright (c) 2022-2024 Siemens AG Oesterreich
# SPDX-License-Identifier: MIT

import os
import datetime

from typing import List

from clingo import Control

ELEMENT_TYPES = 4
ELEMENT_NAMES = 'ABCD'

domain_sizes = [19, 33, 51, 65, 84, 98, 116, 130, 149, 163, 181, 195, 214, 228, 246, 260, 279, 293, 311, 325]
o_instances = [x+1 for x in range(20)]


def generate_ids(n: int) -> List:
    """
    Generates combinations of element definitions
    with suitable IDs.
    """

    ids = [id+1 for id in range(ELEMENT_TYPES*n)]
    assigned = [ids[i*n:i*n+n] for i in range(ELEMENT_TYPES)]
    terms = []

    for letter, category in enumerate(assigned):
        for id in category:
            terms.append(f"ooasp_isa(element{ELEMENT_NAMES[letter]},{id}).")

    return terms


def rewrite_assumptions(content: List[str], save: bool = True) -> None:
    """
    Rewrites the assumptions.lp file to the list of content passed.
    If save is set to true, creates a legacy directory and saves a copy of existing assumptions to it.
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


def add_domain(n: int) -> None:
    """
    Adds domain size constraints to the assumption file
    """
    with open('instances/assumptions.lp', 'a') as file:
        t = f'ooasp_domain(object,1..{n}).'
        file.write(t)


def build_assumptions(n: int, save: bool = False) -> None:
    """
    Builds the new assumptions file in its entirety.
    """
    ts = generate_ids(n)
    rewrite_assumptions(ts, save=save)
    add_domain(domain_sizes[n-1] if len(domain_sizes) >= n else 100)


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


def log_model(model, out=False):
    """
    Creates a model directory (if it does not exist)
    And logs resulting models into files
    """
    os.makedirs('results/models', exist_ok=True)

    global timestr
    new_file = f"results/models/M{iteration}{timestr}.txt"
    with open(new_file, 'w') as mfile:
        mfile.write(str(model))
        if out:
            print('MODEL:')
            print(model)


def log_results(stats: str, iteration: int, out: bool=False):
    """
    Creates a results directory (if it does not exist)
    And logs times and results into text files.
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
    global model
    model = None
    global timestr
    timestr = str(datetime.datetime.now()).replace(' ', '_').replace('.', '-').replace(':', '-')
    for iteration in o_instances:
        print(f">>Solving for:{iteration}")
        build_assumptions(iteration)
        ctl = reset_solving()
        ctl.solve(on_model=on_model)
        log_results(str(ctl.statistics['summary']['times']),iteration, out=True)
