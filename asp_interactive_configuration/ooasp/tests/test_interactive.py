# Copyright (c) 2022 Siemens AG Oesterreich
# SPDX-License-Identifier: MIT

import pytest
from clingo import parse_term
from ooasp.kb import OOASPKnowledgeBase
from ooasp.interactive import InteractiveConfigurator
from ooasp import settings


import pytest
from importlib import reload
@pytest.fixture(autouse=True)
def overwrite_settings():
    settings = reload(__import__("ooasp").settings)
    settings.init('basic')
    yield

def test_interactive_extend_browse():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    iconf = InteractiveConfigurator(racks_kb,"i1")
    iconf.extend_domain(5)
    assert iconf.domain_size == 5
    found = iconf.next_solution()
    assert found
    assert "ooasp_domain(i1,object,1)." in iconf.config.fb.asp_str()
    assert "ooasp_domain(i1,object,3)." in iconf.config.fb.asp_str()
    assert "ooasp_domain(i1,object,4)." in iconf.config.fb.asp_str()
    assert "ooasp_domain(i1,object,5)." in iconf.config.fb.asp_str()
    found = iconf.next_solution()
    assert found
    q = found.associations
    assert len(q)==4
    q = iconf.found_config.associations
    assert len(q)==4


def test_interactive_add_leaf_non_leafclass():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    iconf = InteractiveConfigurator(racks_kb,"i1")

    with pytest.raises(Exception) as e_info:
        iconf.new_object('module')
    assert iconf.domain_size == 0

def test_interactive_add_leaf_extend_browse():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    iconf = InteractiveConfigurator(racks_kb,"i1")

    iconf.new_object('frame')
    found = iconf.next_solution()
    assert not found
    assert parse_term("ooasp_isa_leaf(i1,frame,1)") in  iconf.state.config.assumptions
    assert iconf.domain_size == 1

    iconf.extend_domain(4)
    assert iconf.domain_size == 5
    found = iconf.next_solution()
    assert found
    assert "ooasp_domain(i1,object,1)." in iconf.config.fb.asp_str()
    assert "ooasp_isa_leaf(i1,frame,1)." in iconf.config.fb.asp_str()
    assert "ooasp_domain(i1,object,3)." in iconf.config.fb.asp_str()
    assert "ooasp_domain(i1,object,4)." in iconf.config.fb.asp_str()
    assert "ooasp_domain(i1,object,5)." in iconf.config.fb.asp_str()
    found = iconf.next_solution()


def test_interactive_extend_incrementally():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    iconf = InteractiveConfigurator(racks_kb,"i1")
    iconf.new_object('frame')
    found = iconf.extend_incrementally()
    assert found
    assert iconf.domain_size == 5
    assert "ooasp_domain(i1,object,1)." in iconf.config.fb.asp_str()
    assert "ooasp_isa_leaf(i1,frame,1)." in iconf.config.fb.asp_str()
    assert "ooasp_domain(i1,object,3)." in iconf.config.fb.asp_str()
    assert "ooasp_domain(i1,object,4)." in iconf.config.fb.asp_str()
    assert "ooasp_domain(i1,object,5)." in iconf.config.fb.asp_str()
    found = iconf.next_solution()
    assert found
    assert len(iconf.states)==3

def test_interactive_select_full():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    iconf = InteractiveConfigurator(racks_kb,"i1")
    iconf.new_object('frame')
    found = iconf.extend_incrementally()
    assert found
    assert iconf.domain_size == 5
    iconf.select_found_configuration()
    iconf.new_object('frame')
    found_new = iconf.next_solution()
    for f in found.fb:
        assert str(f) in found_new.fb.asp_str()

    assert "ooasp_isa_leaf(i1,frame,6)." in found_new.fb.asp_str()

def test_interactive_check():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    iconf = InteractiveConfigurator(racks_kb,"i1")
    iconf.check()
    assert len(iconf.config.constraint_violations) == 0
    iconf.new_object('frame')
    iconf.new_object('frame')
    iconf.new_object('frame')
    iconf.check()
    assert len(iconf.config.constraint_violations) == 6
    assert 'ooasp_cv(i1,lowerbound,1,"Lowerbound for association {} not reached: {}",(rack_frames,1,3)).' in iconf.state.config.fb.asp_str()
    assert 'ooasp_cv(i1,lowerbound,2,"Lowerbound for association {} not reached: {}",(rack_frames,1,3)).' in iconf.state.config.fb.asp_str()
    assert 'ooasp_cv(i1,lowerbound,3,"Lowerbound for association {} not reached: {}",(rack_frames,1,3)).' in iconf.state.config.fb.asp_str()
    assert 'ooasp_cv(i1,no_value,1,"Missing value for {}",(frame_position,))' in iconf.state.config.fb.asp_str()
    assert 'ooasp_cv(i1,no_value,2,"Missing value for {}",(frame_position,))' in iconf.state.config.fb.asp_str()
    assert 'ooasp_cv(i1,no_value,3,"Missing value for {}",(frame_position,))' in iconf.state.config.fb.asp_str()


def test_interactive_check_custom_cv():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    iconf = InteractiveConfigurator(racks_kb,"i1",[settings.racks_example_constraints])
    iconf.check()
    assert len(iconf.config.constraint_violations) == 0
    iconf.new_object('frame')
    iconf.check()
    found = iconf.extend_incrementally()
    iconf.select_found_configuration()
    iconf.new_object('frame')
    iconf.select_association('rack_frames',5,6)
    iconf.check()
    assert 'ooasp_cv(i1,racksingleupperbound,5,"Rack singles should be associated to 4 frames ",(6,)).' in iconf.state.config.fb.asp_str()



def test_interactive_select():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    iconf = InteractiveConfigurator(racks_kb,"i1",[settings.racks_example_constraints])
    iconf.extend_domain(1)
    iconf.select_object_class(1,'frame')
    leafs = iconf.config.leafs
    assert len(leafs)==1
    assert leafs[0].object_id==1
    assert leafs[0].class_name=='frame'
    iconf.select_object_class(1,'rackDouble')
    leafs = iconf.config.leafs
    assert len(leafs)==1
    assert leafs[0].object_id==1
    assert leafs[0].class_name=='rackDouble'
    found = iconf.extend_incrementally()
    assert found.domain_size == 9
    assert "ooasp_isa_leaf(i1,rackDouble,1)." in found.fb.asp_str()
    iconf.select_found_configuration()
    passed = iconf.check()
    assert passed
    iconf.select_value(2,'frame_position',4)
    iconf.select_value(3,'frame_position',4)
    passed = iconf.check()
    assert not passed



def test_options():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    iconf = InteractiveConfigurator(racks_kb,"i1",[settings.racks_example_constraints])
    iconf.extend_domain(1)

    brave_conf = iconf.get_options()
    conf_str = brave_conf.fb.asp_str()
    leafs = ["frame", "moduleI", "moduleII", "moduleIII", "moduleIV", "moduleV", "elementA", "elementB", "elementC", "elementD", "rackSingle", "rackDouble"]
    for l in leafs:
        assert f"ooasp_isa_leaf(i1,{l},1)." in conf_str
    iconf.extend_domain(1)
    iconf.select_object_class(1,'frame')
    iconf.select_value(1,'frame_position',4)
    brave_conf = iconf.get_options()
    opts = iconf._brave_config_as_options()
    opt = [o['str'] for x in opts.values() for o in x]
    assert 1 in opts

    assert "remove_leaf_class(1)" in opt
    assert "remove_value(1, 'frame_position')" in opt
    assert "select_association('rack_frames', 2, 1)" in opt
    assert "select_association('frame_modules', 1, 2)" in opt

    assert 2 in opts
    assert "select_object_class(2, 'frame')" in opt
    assert "select_object_class(2, 'moduleI')" in opt
    assert "select_object_class(2, 'moduleII')" in opt
    assert "select_object_class(2, 'moduleIII')" in opt
    assert "select_object_class(2, 'moduleIV')" in opt
    assert "select_object_class(2, 'moduleV')" in opt
    assert "select_object_class(2, 'elementA')" in opt
    assert "select_object_class(2, 'elementB')" in opt
    assert "select_object_class(2, 'elementC')" in opt
    assert "select_object_class(2, 'elementD')" in opt
    assert "select_object_class(2, 'rackSingle')" in opt
    assert "select_object_class(2, 'rackDouble')" in opt
    assert "select_value(2, 'frame_position', 1)" in opt
    assert "select_value(2, 'frame_position', 2)" in opt
    assert "select_value(2, 'frame_position', 3)" in opt
    assert "select_value(2, 'frame_position', 4)" in opt
    assert "select_value(2, 'frame_position', 5)" in opt
    assert "select_value(2, 'frame_position', 6)" in opt
    assert "select_value(2, 'frame_position', 7)" in opt
    assert "select_value(2, 'frame_position', 8)" in opt
    assert "select_association('rack_frames', 2, 1)" in opt
    assert "select_association('frame_modules', 1, 2)" in opt

    iconf.select_association('rack_frames', 2, 1)

    brave_conf = iconf.get_options()
    opts = iconf._brave_config_as_options()
    opt = [o['str'] for x in opts.values() for o in x]
    assert "remove_association('rack_frames', 2, 1)" in opt


def test_json():

    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    print(racks_kb)
    iconf = InteractiveConfigurator(racks_kb,"i1",[settings.racks_example_constraints])
    print(iconf)