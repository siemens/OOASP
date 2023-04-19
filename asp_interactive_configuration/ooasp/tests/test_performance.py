# Copyright (c) 2022 Siemens AG Oesterreich
# SPDX-License-Identifier: MIT

from ooasp.interactive import InteractiveConfigurator
from ooasp.kb import OOASPKnowledgeBase

def test_solve_multiple_elements():
    """ create elements and solve under 30 seconds """

    racks_kb = OOASPKnowledgeBase.from_file("racks_v1","./examples/racks/kb.lp")
    iconf = InteractiveConfigurator(racks_kb,"i1",["./examples/racks/constraints.lp"])
    # current limit
    nr_of_elements = 18
    for i in range(nr_of_elements):
        iconf.new_leaf("elementA")
    iconf.extend_domain(nr_of_elements + 5)
    config = iconf.next_solution()
    assert len(config.constraint_violations)==0
    assert iconf._time_grounding+iconf._time_solving < 30

def test_solve_multiple_racks_incremental():
    """ create elements and solve under 30 seconds """

    racks_kb = OOASPKnowledgeBase.from_file("racks_v1","./examples/racks/kb.lp")
    iconf = InteractiveConfigurator(racks_kb,"i1",["./examples/racks/constraints.lp"])
    # current limit
    nr_of_racks = 3
    for i in range(nr_of_racks):
        iconf.new_leaf("rackSingle")
    config = iconf.extend_incrementally()
    print(iconf._statistics)
    assert len(config.constraint_violations)==0
    assert iconf._time_grounding+iconf._time_solving < 30

