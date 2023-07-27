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
    settings.init('defined')
    yield

def test_s_interactive_extend_browse():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    iconf = InteractiveConfigurator(racks_kb,"i1")
    iconf.extend_domain(2,cls='element')
    brave = iconf.get_options()
    conf_str = brave.fb.asp_str()
    element_leafs = ["elementA", "elementB", "elementC", "elementD"]
    other_leafs = ["frame", "moduleI", "moduleII", "moduleIII", "moduleIV", "moduleV", "rackSingle", "rackDouble"]
    for l in element_leafs:
        assert f"ooasp_isa_leaf({l},1)." in conf_str
    for l in other_leafs:
        assert not f"ooasp_isa_leaf({l},1)." in conf_str



def test_s_interactive_extend_browse():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    iconf = InteractiveConfigurator(racks_kb,"i1")
    iconf.extend_domain(5)
    assert iconf.domain_size == 5
    found = iconf.next_solution()
    assert found
    assert "ooasp_domain(object,1)." in iconf.config.fb.asp_str()
    assert "ooasp_domain(object,3)." in iconf.config.fb.asp_str()
    assert "ooasp_domain(object,4)." in iconf.config.fb.asp_str()
    assert "ooasp_domain(object,5)." in iconf.config.fb.asp_str()
    found = iconf.next_solution()
    assert found
    q = found.associations
    assert len(q)==4
    q = iconf.found_config.associations
    assert len(q)==4


def test_s_interactive_add_leaf_non_class():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    iconf = InteractiveConfigurator(racks_kb,"i1")

    with pytest.raises(Exception) as e_info:
        iconf.new_object('other')
    assert iconf.domain_size == 0

def test_s_interactive_add_leaf_extend_browse():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    iconf = InteractiveConfigurator(racks_kb,"i1")

    iconf.new_object('frame')
    found = iconf.next_solution()
    assert not found
    assert parse_term("ooasp_isa(frame,1)") in  iconf.state.config.assumptions
    assert iconf.domain_size == 1

    iconf.extend_domain(4)
    assert iconf.domain_size == 5
    found = iconf.next_solution()
    assert found
    assert "ooasp_domain(frame,1)." in found.fb.asp_str()
    assert "ooasp_isa_leaf(frame,1)." in found.fb.asp_str()
    assert "ooasp_domain(object,3)." in found.fb.asp_str()
    assert "ooasp_domain(object,4)." in found.fb.asp_str()
    assert "ooasp_domain(object,5)." in found.fb.asp_str()
    found = iconf.next_solution()

def test_s_interactive_add_object_extend_browse():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    iconf = InteractiveConfigurator(racks_kb,"i1")

    iconf.new_object('rack')
    found = iconf.next_solution()
    assert not found
    assert parse_term("ooasp_isa(rack,1)") in  iconf.state.config.assumptions
    assert iconf.domain_size == 1

    iconf.extend_domain(4)
    assert iconf.domain_size == 5
    found = iconf.next_solution()
    assert found
    assert "ooasp_domain(rack,1)." in found.fb.asp_str()
    assert "ooasp_isa_leaf(rackSingle,1)." in found.fb.asp_str()
    assert "ooasp_domain(object,3)." in found.fb.asp_str()
    assert "ooasp_domain(object,4)." in found.fb.asp_str()
    assert "ooasp_domain(object,5)." in found.fb.asp_str()
    assert "ooasp_isa_leaf(frame,2)." in found.fb.asp_str()
    assert "ooasp_isa_leaf(frame,3)." in found.fb.asp_str()
    assert "ooasp_isa_leaf(frame,4)." in found.fb.asp_str()

def test_s_interactive_extend_incrementally():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    iconf = InteractiveConfigurator(racks_kb,"i1")
    iconf.new_object('frame')
    found = iconf.extend_incrementally()
    assert found
    assert iconf.domain_size == 5
    assert "ooasp_domain(frame,1)." in found.fb.asp_str()
    assert "ooasp_isa_leaf(frame,1)." in found.fb.asp_str()
    assert "ooasp_domain(object,2)." in found.fb.asp_str()
    assert "ooasp_domain(object,3)." in found.fb.asp_str()
    assert "ooasp_domain(object,4)." in found.fb.asp_str()
    assert "ooasp_domain(object,5)." in found.fb.asp_str()
    found = iconf.next_solution()
    assert found
    assert len(iconf.states)==3

def test_s_interactive_extend_incrementally_overshooting():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    iconf = InteractiveConfigurator(racks_kb,"i1")
    iconf.new_object('frame')
    found = iconf.extend_incrementally(overshoot=True)
    assert found
    assert iconf.domain_size == 5
    assert "ooasp_domain(frame,1)." in found.fb.asp_str()
    assert "ooasp_isa_leaf(frame,1)." in found.fb.asp_str()
    assert "ooasp_domain(rack,2)." in found.fb.asp_str()
    assert "ooasp_domain(object,3)." in found.fb.asp_str()
    assert "ooasp_domain(object,4)." in found.fb.asp_str()
    assert "ooasp_domain(object,5)." in found.fb.asp_str()
    print(iconf)
    found = iconf.next_solution()
    assert found
    print(found)
    assert len(iconf.states)==3

def test_s_interactive_extend_incrementally_overshooting_leaving_object():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    iconf = InteractiveConfigurator(racks_kb,"i1")
    iconf.new_object('frame')
    iconf.new_object('frame')
    found = iconf.extend_incrementally(overshoot=True)
    assert found
    assert iconf.domain_size == 6
    assert "ooasp_domain(frame,1)." in found.fb.asp_str()
    assert "ooasp_isa_leaf(frame,1)." in found.fb.asp_str()
    assert "ooasp_domain(frame,2)." in found.fb.asp_str()
    assert "ooasp_domain(rack,3)." in found.fb.asp_str()
    assert "ooasp_domain(rack,4)." in found.fb.asp_str()
    found = iconf.next_solution()
    print(found)
    assert found
    assert not "ooasp_isa_leaf(rack,4)." in found.fb.asp_str() or  not "ooasp_isa_leaf(rack,3)." in found.fb.asp_str()
    assert found.size == 5
    assert len(iconf.states)==4


def test_s_interactive_select_full():
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

    assert "ooasp_isa_leaf(frame,6)." in found_new.fb.asp_str()

def test_s_interactive_ccheck():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    iconf = InteractiveConfigurator(racks_kb,"i1")
    iconf.check()
    assert len(iconf.config.constraint_violations) == 0
    iconf.new_object('frame')
    iconf.new_object('frame')
    iconf.new_object('frame')
    iconf.check()
    assert len(iconf.config.constraint_violations) == 6
    assert 'ooasp_cv(lowerbound,1,"Lowerbound for association {} not reached: {}",(rack_frames,1,3)).' in iconf.state.config.fb.asp_str()
    assert 'ooasp_cv(lowerbound,2,"Lowerbound for association {} not reached: {}",(rack_frames,1,3)).' in iconf.state.config.fb.asp_str()
    assert 'ooasp_cv(lowerbound,3,"Lowerbound for association {} not reached: {}",(rack_frames,1,3)).' in iconf.state.config.fb.asp_str()
    assert 'ooasp_cv(no_value,1,"Missing value for {}",(frame_position,))' in iconf.state.config.fb.asp_str()
    assert 'ooasp_cv(no_value,2,"Missing value for {}",(frame_position,))' in iconf.state.config.fb.asp_str()
    assert 'ooasp_cv(no_value,3,"Missing value for {}",(frame_position,))' in iconf.state.config.fb.asp_str()


def test_s_interactive_check_custom_cv():
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
    assert 'ooasp_cv(racksingleupperbound,5,"Rack singles should be associated to 4 frames ",(6,)).' in iconf.state.config.fb.asp_str()



def test_s_interactive_select():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    iconf = InteractiveConfigurator(racks_kb,"i1",[settings.racks_example_constraints])
    iconf.extend_domain(1)
    iconf.select_object_class(1,'frame')
    objects = iconf.config.objects
    assert len(objects)==1
    assert objects[0].object_id==1
    assert objects[0].class_name=='frame'
    iconf.select_object_class(1,'rackDouble')
    objects = iconf.config.objects
    assert len(objects)==1
    assert objects[0].object_id==1
    assert objects[0].class_name=='rackDouble'
    found = iconf.extend_incrementally()
    assert found.domain_size == 9
    assert "ooasp_isa_leaf(rackDouble,1)." in found.fb.asp_str()
    iconf.select_found_configuration()
    passed = iconf.check()
    assert passed
    iconf.select_value(2,'frame_position',4)
    iconf.select_value(3,'frame_position',4)
    passed = iconf.check()
    assert not passed





def test_s_options():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    iconf = InteractiveConfigurator(racks_kb,"i1",[settings.racks_example_constraints])
    iconf.extend_domain(1)

    brave_conf = iconf.get_options()
    conf_str = brave_conf.fb.asp_str()
    leafs = ["frame", "moduleI", "moduleII", "moduleIII", "moduleIV", "moduleV", "elementA", "elementB", "elementC", "elementD", "rackSingle", "rackDouble"]
    for l in leafs:
        assert f"ooasp_isa_leaf({l},1)." in conf_str
    iconf.extend_domain(1)
    iconf.select_object_class(1,'frame')
    iconf.select_value(1,'frame_position',4)
    brave_conf = iconf.get_options()
    opts = iconf._brave_config_as_options()
    opt = [o['str'] for x in opts.values() for o in x]
    assert 1 in opts
    assert "remove_object_class(1)" in opt
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


def test_s_json():

    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    iconf = InteractiveConfigurator(racks_kb,"i1",[settings.racks_example_constraints])




def test_normal_extend():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    iconf = InteractiveConfigurator(racks_kb,"i1")
    iconf.new_object('rackSingle')
    found = iconf.extend_incrementally()
    found_str = found.fb.asp_str()

    assert found
    assert iconf.domain_size == 5
    assert "ooasp_domain(rackSingle,1)." in found_str
    assert "ooasp_isa_leaf(rackSingle,1)." in found_str

def test_extend_propagate():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    iconf = InteractiveConfigurator(racks_kb,"i1")
    iconf.extend_domain(1,cls='rackSingle',propagate=True)
    iconf.select_object_class(1, 'rackSingle')
    iconf.select_object_class(2, 'frame')
    iconf.select_object_class(3, 'frame')
    iconf.select_object_class(4, 'frame')
    iconf.select_object_class(5, 'frame')
    conf_str = iconf.config.fb.asp_str()
    assert 'ooasp_domain(rackSingle,1).' in conf_str
    assert 'ooasp_domain(frame,2).'  in conf_str
    assert 'ooasp_domain(frame,3).'  in conf_str
    assert 'ooasp_domain(frame,4).'  in conf_str
    assert 'ooasp_domain(frame,5).'  in conf_str
    iconf.check()
    found = iconf.next_solution()
    assert found

    # found = iconf.extend_incrementally()
    conf_str = found.fb.asp_str()
    assert 'ooasp_isa_leaf(rackSingle,1).' in conf_str
    assert 'ooasp_isa_leaf(frame,2).' in conf_str
    assert 'ooasp_associated(rack_frames,1,2).'  in conf_str
    assert 'ooasp_associated(rack_frames,1,3).'  in conf_str
    assert 'ooasp_associated(rack_frames,1,4).'  in conf_str
    assert 'ooasp_associated(rack_frames,1,5)'  in conf_str

    # iconf = InteractiveConfigurator(racks_kb,"i1")
    # iconf.extend_domain(1,cls='element',propagate=True)
    # iconf.select_object_class(1, 'element')
    # conf_str = iconf.config.fb.asp_str()
    # assert 'ooasp_domain(element,1).' in conf_str
    # assert 'ooasp_domain(module,2).' in conf_str
    # assert 'ooasp_domain(frame,3).' in conf_str
    # assert 'ooasp_domain(rack,4).' in conf_str
    # assert 'ooasp_associated(rack_frames,3,4).' in conf_str
    # assert 'ooasp_associated(frame_modules,2,3).' in conf_str
    # assert 'ooasp_associated(element_modules,1,2)' in conf_str

def test_extend_propagate_empty():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    iconf = InteractiveConfigurator(racks_kb,"i1")
    iconf.extend_domain(1,cls='rackSingle',propagate=True)
    conf_str = iconf.config.fb.asp_str()
    assert 'ooasp_domain(rackSingle,1).' in conf_str
    assert 'ooasp_domain(frame,2).'  in conf_str
    assert 'ooasp_domain(frame,3).'  in conf_str
    assert 'ooasp_domain(frame,4).'  in conf_str
    assert 'ooasp_domain(frame,5).'  in conf_str
    iconf.check()
    found = iconf.next_solution()
    assert found
    found = iconf.next_solution()
    assert found

def test_extend_propagate_symmetry():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    iconf = InteractiveConfigurator(racks_kb,"i1")
    # iconf.extend_domain(5,cls='object',propagate=True)
    iconf.extend_domain(1,cls='rackSingle')
    iconf.extend_domain(4,cls='frame')
    found = iconf.next_solution()
    assert found
    found = iconf.next_solution()
    assert found


    iconf = InteractiveConfigurator(racks_kb,"i1")
    iconf.extend_domain(4,cls='frame')
    iconf.extend_domain(1,cls='rackSingle')
    found = iconf.next_solution()
    assert found
    found = iconf.next_solution()
    assert found

def test_create_required_objects():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    iconf = InteractiveConfigurator(racks_kb,"i1")
    # iconf.extend_domain(5,cls='object',propagate=True)
    iconf.extend_domain(1,cls='rackSingle')
    iconf.extend_domain(3,cls='frame')
    iconf.select_association('rack_frames',1,2)
    iconf.select_association('rack_frames',1,3)
    iconf.select_association('rack_frames',1,4)
    found = iconf.next_solution()
    assert not found
    config_str = iconf.config.fb.asp_str()
    assert "ooasp_associated(rack_frames,1,2)." in config_str
    assert "ooasp_associated(rack_frames,1,3)." in config_str
    assert "ooasp_associated(rack_frames,1,4)." in config_str
    iconf._create_required_objects('rackSingle',1)
    config_str = iconf.config.fb.asp_str()
    assert "ooasp_domain(frame,5)." in config_str
    found = iconf.next_solution()
    assert found


def test_custom_interactive_add_leaf_extend_browse():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    iconf = InteractiveConfigurator(racks_kb,"i1")

    iconf.new_object('frame')
    found = iconf.next_solution()
    assert not found
    assert parse_term("ooasp_isa(frame,1)") in  iconf.state.config.assumptions
    assert iconf.domain_size == 1

    iconf.extend_domain(3,'frame')
    iconf.extend_domain(1,'rack')
    assert iconf.domain_size == 5
    found = iconf.next_solution()
    assert found
    assert "ooasp_domain(frame,1)." in found.fb.asp_str()
    assert "ooasp_isa_leaf(frame,1)." in found.fb.asp_str()
    assert "ooasp_domain(frame,3)." in found.fb.asp_str()
    assert "ooasp_domain(frame,4)." in found.fb.asp_str()
    assert "ooasp_domain(rack,5)." in found.fb.asp_str()
    found = iconf.next_solution()
    assert found

def test_not_a_subclass():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    iconf = InteractiveConfigurator(racks_kb,"i1")

    iconf.extend_domain(1,'rackSingle')
    iconf.select_object_class(1, 'rackDouble')
    ok = iconf.check()
    assert ok # Its ok because the rackDouble is ignored since it no external is grounded for user(ooasp_isa(1,rackDouble))

def test_add_remove_assoc():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    iconf = InteractiveConfigurator(racks_kb,"i1")
    
    iconf.extend_domain(1,'object')
    iconf.extend_domain(1,'object')
    brave_conf = iconf.get_options()
    brave_str = brave_conf.fb.asp_str()
    assert "ooasp_isa(frame,1)." in brave_str
    assert "ooasp_isa(module,1)." in brave_str
    assert "ooasp_isa(frame,2)." in brave_str
    assert "ooasp_isa(module,2)." in brave_str
    assert "user(" not in brave_str

    iconf.select_association('frame_modules',1,2)
    iconf.check()
    checked_str = iconf.config.fb.asp_str()
    assert "ooasp_associated(frame_modules,1,2)." in checked_str

    iconf.remove_association('frame_modules',1,2)
    iconf.check()
    checked_str = iconf.config.fb.asp_str()
    assert "ooasp_associated(frame_modules,1,2)." not in checked_str

    iconf.select_association('frame_modules',1,2)
    iconf.check()
    checked_str = iconf.config.fb.asp_str()
    brave_conf = iconf.get_options()
    brave_str = brave_conf.fb.asp_str()
    assert "user(ooasp_associated(frame_modules,1,2))." in brave_str
    assert "ooasp_isa(module,2)." in brave_str
    assert "ooasp_isa(frame,2)." not in brave_str
    assert "ooasp_isa(element,2)." not in brave_str

    assert "ooasp_isa(frame,1)." in brave_str
    assert "ooasp_isa(module,1)." not in brave_str
    assert "ooasp_isa(element,1)." not in brave_str


def test_three_racks():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    iconf = InteractiveConfigurator(racks_kb,"i1")

    iconf.new_object('rackSingle')
    iconf.new_object('rackSingle')
    iconf.new_object('rackSingle')
    found = iconf.extend_incrementally()
    found.save_png(directory="./out/test")
