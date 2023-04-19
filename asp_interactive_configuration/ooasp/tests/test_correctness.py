# Copyright (c) 2022 Siemens AG Oesterreich
# SPDX-License-Identifier: MIT

from ooasp.interactive import InteractiveConfigurator
from ooasp.kb import OOASPKnowledgeBase

def test_racks_constraints_element():
    """ test element constraints """
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1","./examples/racks/kb.lp")
    iconf = InteractiveConfigurator(racks_kb,"i1",["./examples/racks/constraints.lp"])
    iconf.new_leaf("elementA")
    iconf.check()
    assert len(iconf.config.constraint_violations)==2
    assert "lowerbound" in str(iconf.config.constraint_violations)
    assert "customlowerbound" in str(iconf.config.constraint_violations)

def test_racks_constraints_module():
    """ test module constraints """
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1","./examples/racks/kb.lp")
    iconf = InteractiveConfigurator(racks_kb,"i1",["./examples/racks/constraints.lp"])
    iconf.new_leaf("moduleI")
    iconf.check()
    assert len(iconf.config.constraint_violations)==2
    assert "lowerbound" in str(iconf.config.constraint_violations)
    assert "module_requires_element" in str(iconf.config.constraint_violations)

def test_racks_constraints_moduleV():
    """ the moduleV constraints """
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1","./examples/racks/kb.lp")
    iconf = InteractiveConfigurator(racks_kb,"i1",["./examples/racks/constraints.lp"])
    iconf.new_leaf("moduleV")
    iconf.check()
    assert len(iconf.config.constraint_violations)==1
    assert "lowerbound" in str(iconf.config.constraint_violations)

def test_racks_constraints_frame():
    """ test frame constraints """
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1","./examples/racks/kb.lp")
    iconf = InteractiveConfigurator(racks_kb,"i1",["./examples/racks/constraints.lp"])
    iconf.new_leaf("frame")
    iconf.check()
    assert len(iconf.config.constraint_violations)==2
    assert "no_value" in str(iconf.config.constraint_violations)
    assert "lowerbound" in str(iconf.config.constraint_violations)

def test_racks_constraints_rack():
    """ test rack constraints """
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1","./examples/racks/kb.lp")
    iconf = InteractiveConfigurator(racks_kb,"i1",["./examples/racks/constraints.lp"])
    iconf.new_leaf("rackSingle")
    iconf.check()
    assert len(iconf.config.constraint_violations)==2
    assert "lowerbound" in str(iconf.config.constraint_violations)
    assert "racksinglelowerbound" in str(iconf.config.constraint_violations)
    iconf.new_leaf("rackDouble")
    iconf.check()
    assert len(iconf.config.constraint_violations)==4
    assert "rackdoublelowerbound" in str(iconf.config.constraint_violations)


def test_racks_constraints_associations():
    """ test assoc constraints """
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1","./examples/racks/kb.lp")
    iconf = InteractiveConfigurator(racks_kb,"i1",["./examples/racks/constraints.lp"])
    iconf.new_leaf("moduleV")
    iconf.new_leaf("elementA")
    iconf.select_association("element_modules",2,1)
    iconf.check()
    assert len(iconf.config.constraint_violations)==2
    assert "assoc1_constraint1" in str(iconf.config.constraint_violations)

    racks_kb = OOASPKnowledgeBase.from_file("racks_v1","./examples/racks/kb.lp")
    iconf = InteractiveConfigurator(racks_kb,"i1",["./examples/racks/constraints.lp"])
    iconf.new_leaf("elementA")
    iconf.new_leaf("moduleV")
    iconf.select_association("element_modules",1,2)
    iconf.check()
    assert len(iconf.config.constraint_violations)==2
    assert "assoc1_constraint2" in str(iconf.config.constraint_violations)

def test_racks_constraints_moduleII_requires_moduleV():
    """ test moduleII requires moduleV constraint """
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1","./examples/racks/kb.lp")
    iconf = InteractiveConfigurator(racks_kb,"i1",["./examples/racks/constraints.lp"])
    iconf.new_leaf("frame")
    iconf.new_leaf("moduleII")
    iconf.new_leaf("moduleV")

    iconf.select_association("frame_modules",1,2)
    iconf.check()
    assert len(iconf.config.constraint_violations)==5
    assert "moduleII_requires_moduleV" in str(iconf.config.constraint_violations)

    iconf.select_association("frame_modules",1,3)
    iconf.check()
    assert len(iconf.config.constraint_violations)==3
    assert "moduleII_requires_moduleV" not in str(iconf.config.constraint_violations)

    racks_kb = OOASPKnowledgeBase.from_file("racks_v1","./examples/racks/kb.lp")
    iconf = InteractiveConfigurator(racks_kb,"i1",["./examples/racks/constraints.lp"])
    iconf.new_leaf("frame")
    iconf.new_leaf("moduleV")
    iconf.new_leaf("moduleII")

    iconf.select_association("frame_modules",1,2)
    iconf.check()
    assert len(iconf.config.constraint_violations)==5
    assert "moduleII_requires_moduleV" in str(iconf.config.constraint_violations)

    iconf.select_association("frame_modules",1,3)
    iconf.check()
    assert len(iconf.config.constraint_violations)==3
    assert "moduleII_requires_moduleV" not in str(iconf.config.constraint_violations)


def test_solve_elements():
    """ solve one instance of each element type"""
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1","./examples/racks/kb.lp")
    element_configuration_size = { "elementA":7, "elementB":9, "elementC":9,"elementD":10}
    for element_type in element_configuration_size.keys():
        iconf = InteractiveConfigurator(racks_kb,"i1",["./examples/racks/constraints.lp"])
        iconf.new_leaf(element_type)
        config = iconf.extend_incrementally()
        assert len(config.constraint_violations)==0
        assert config.domain_size == element_configuration_size[element_type]



