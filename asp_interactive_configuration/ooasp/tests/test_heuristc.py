# Copyright (c) 2022 Siemens AG Oesterreich
# SPDX-License-Identifier: MIT

from ooasp.interactive import InteractiveConfigurator
from ooasp.kb import OOASPKnowledgeBase
from ooasp import settings
from ooasp.tests.utils import new_racks_iconf

from importlib import reload

def test_heuristic():
    """ test element constraints """
    iconf = new_racks_iconf()
    iconf.extend_domain(6)
    # First empty
    found = iconf.next_solution()
    assert found
    assert found.size == 0
    # Then the combinations of all frame positions
    for i in range(0,24):
        found = iconf.next_solution()
        print(found)
        assert found
        assert found.size == 5
        assert "ooasp_isa_leaf(rackSingle,5)." in found.fb.asp_str()
    found = iconf.next_solution()
    # Then 6 elements
    assert found
    assert found.size == 6
    assert "ooasp_isa_leaf(rackSingle,6)." in found.fb.asp_str()


def test_heuristic_module():
    """ test element constraints """
    iconf = new_racks_iconf()
    iconf.new_object('rackSingle')
    found = iconf.extend_incrementally()
    assert found.size==5
    iconf.select_found_configuration()
    iconf.remove_value(2,'frame_position')
    iconf.remove_value(3,'frame_position')
    iconf.extend_domain(1)
    found = iconf.next_solution()
    assert found.size==5
    found = iconf.next_solution()
    assert found.size==5
    found = iconf.next_solution()
    assert found.size==6
