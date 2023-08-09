# Copyright (c) 2022 Siemens AG Oesterreich
# SPDX-License-Identifier: MIT

from ooasp.interactive import InteractiveConfigurator
from ooasp.kb import OOASPKnowledgeBase
from ooasp import settings
from ooasp.tests.utils import new_racks_iconf

import pytest
from importlib import reload

def test_racks_constraints_element():
    """ test element constraints """
    iconf = new_racks_iconf()
    iconf.new_object("elementA")
    iconf.check()
    assert len(iconf.config.constraint_violations)==2
    assert "lowerbound" in str(iconf.config.constraint_violations)
    assert "customlowerbound" in str(iconf.config.constraint_violations)

def test_racks_constraints_module():
    """ test module constraints """
    iconf = new_racks_iconf()
    iconf.new_object("moduleI")
    iconf.check()
    assert len(iconf.config.constraint_violations)==2
    assert "lowerbound" in str(iconf.config.constraint_violations)
    assert "module_requires_element" in str(iconf.config.constraint_violations)

def test_racks_constraints_moduleV():
    """ the moduleV constraints """
    iconf = new_racks_iconf()
    iconf.new_object("moduleV")
    iconf.check()
    assert len(iconf.config.constraint_violations)==1
    assert "lowerbound" in str(iconf.config.constraint_violations)

def test_racks_constraints_frame():
    """ test frame constraints """
    iconf = new_racks_iconf()
    iconf.new_object("frame")
    iconf.check()
    assert len(iconf.config.constraint_violations)==2
    assert "no_value" in str(iconf.config.constraint_violations)
    assert "lowerbound" in str(iconf.config.constraint_violations)

def test_racks_constraints_rack():
    """ test rack constraints """
    iconf = new_racks_iconf()
    iconf.new_object("rackSingle")
    iconf.check()
    assert len(iconf.config.constraint_violations)==2
    assert "lowerbound" in str(iconf.config.constraint_violations)
    assert "racksinglelowerbound" in str(iconf.config.constraint_violations)
    iconf.new_object("rackDouble")
    iconf.check()
    assert len(iconf.config.constraint_violations)==4
    assert "rackdoublelowerbound" in str(iconf.config.constraint_violations)


def test_racks_constraints_associations():
    """ test assoc constraints """
    iconf = new_racks_iconf()
    iconf.new_object("moduleV")
    iconf.new_object("elementA")
    iconf.select_association("element_modules",2,1)
    iconf.check()
    config_str = iconf.config.fb.asp_str()
    assert "associated(element_modules,2,1)" in config_str

    assert len(iconf.config.constraint_violations)==2
    assert "assoc1_constraint1" in str(iconf.config.constraint_violations)

    iconf = new_racks_iconf()
    iconf.new_object("elementA")
    iconf.new_object("moduleV")
    iconf.select_association("element_modules",1,2)
    iconf.check()
    assert len(iconf.config.constraint_violations)==2
    assert "assoc1_constraint2" in str(iconf.config.constraint_violations)

def test_racks_constraints_moduleII_requires_moduleV():
    """ test moduleII requires moduleV constraint """
    iconf = new_racks_iconf()
    iconf.new_object("frame")
    iconf.new_object("moduleII")
    iconf.new_object("moduleV")

    iconf.select_association("frame_modules",1,2)
    iconf.check()
    assert len(iconf.config.constraint_violations)==5
    assert "moduleII_requires_moduleV" in str(iconf.config.constraint_violations)

    iconf.select_association("frame_modules",1,3)
    iconf.check()

    assert len(iconf.config.constraint_violations)==3
    assert "moduleII_requires_moduleV" not in str(iconf.config.constraint_violations)

    iconf = new_racks_iconf()
    iconf.new_object("frame")
    iconf.new_object("moduleV")
    iconf.new_object("moduleII")

    iconf.select_association("frame_modules",1,3)
    iconf.check()

    assert len(iconf.config.constraint_violations)==5
    assert "moduleII_requires_moduleV" in str(iconf.config.constraint_violations)

    iconf.select_association("frame_modules",1,2)
    iconf.check()

    assert len(iconf.config.constraint_violations)==3
    assert "moduleII_requires_moduleV" not in str(iconf.config.constraint_violations)


def test_solve_elements():
    """ solve one instance of each element type"""
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    element_configuration_size = { "elementA":7, "elementB":9, "elementC":9,"elementD":10}
    for element_type in element_configuration_size.keys():
        iconf = InteractiveConfigurator(racks_kb,"i1",[settings.racks_example_constraints])
        iconf.new_object(element_type)
        config = iconf.extend_incrementally()
        assert len(config.constraint_violations)==0
        assert config.domain_size == element_configuration_size[element_type]



