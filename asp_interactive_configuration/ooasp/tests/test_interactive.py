# Copyright (c) 2022 Siemens AG Oesterreich
# SPDX-License-Identifier: MIT

import pytest
from clingo import parse_term
from ooasp.kb import OOASPKnowledgeBase
from ooasp.interactive import InteractiveConfigurator
from ooasp import settings
from ooasp.tests.utils import new_racks_iconf

import pytest
from importlib import reload

def test_s_interactive_extend_browse_basic():
    iconf = new_racks_iconf()
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
    iconf = new_racks_iconf()
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
    assert len(found.associations)==8 # 4*2
    found = iconf.next_solution()
    assert found
    assert len(found.associations)==8 # 4*2
    found = iconf.next_solution()
    assert found
    assert len(found.associations)==8 # 4*2
    q = iconf.found_config.associations
    assert len(q)==8


def test_s_interactive_add_leaf_non_class():
    iconf = new_racks_iconf()

    with pytest.raises(Exception) as e_info:
        iconf.new_object('other')
    assert iconf.domain_size == 0

def test_s_interactive_add_leaf_extend_browse():
    iconf = new_racks_iconf()

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
    iconf = new_racks_iconf()

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
    iconf = new_racks_iconf()
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
    iconf = new_racks_iconf()
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
    found = iconf.next_solution()
    assert found
    assert len(iconf.states)==3

def test_s_interactive_extend_incrementally_overshooting_rack():
    iconf = new_racks_iconf()
    iconf.new_object('rack')
    found = iconf.extend_incrementally(overshoot=True)
    assert found
    assert iconf.domain_size == 5
    assert "ooasp_domain(rack,1)." in found.fb.asp_str()
    assert "ooasp_isa_leaf(rackSingle,1)." in found.fb.asp_str()
    assert "ooasp_domain(frame,2)." in found.fb.asp_str()
    assert "ooasp_domain(frame,3)." in found.fb.asp_str()
    assert "ooasp_domain(frame,4)." in found.fb.asp_str()
    assert "ooasp_domain(frame,5)." in found.fb.asp_str()
    
    iconf.select_found_configuration()
    iconf.new_object('rack')
    found = iconf.extend_incrementally(overshoot=True)
    assert found
    assert iconf.domain_size == 10



def test_s_interactive_extend_incrementally_overshooting_leaving_object():
    iconf = new_racks_iconf()
    iconf.new_object('frame')
    iconf.new_object('frame')
    found = iconf.extend_incrementally(overshoot=True)
    assert found
    assert iconf.domain_size == 5
    assert "ooasp_domain(frame,1)." in found.fb.asp_str()
    assert "ooasp_isa_leaf(frame,1)." in found.fb.asp_str()
    assert "ooasp_domain(frame,2)." in found.fb.asp_str()
    assert "ooasp_domain(rack,3)." in found.fb.asp_str()
    assert "ooasp_domain(object,4)." in found.fb.asp_str()
    assert found.size == 5


def test_s_interactive_select_full():
    iconf = new_racks_iconf()
    iconf.new_object('frame')
    found = iconf.extend_incrementally()
    assert found
    assert iconf.domain_size == 5
    iconf.select_found_configuration()
    iconf.new_object('module')
    found_new = iconf.next_solution()
    for f in found.fb:
        if not 'user' in str(f):
            assert str(f) in found_new.fb.asp_str()

    assert "ooasp_isa(module,6)." in found_new.fb.asp_str()


def test_s_interactive_ccheck():
    iconf = new_racks_iconf()
    iconf.check()
    assert len(iconf.config.constraint_violations) == 0
    iconf.new_object('frame')
    iconf.new_object('frame')
    iconf.new_object('frame')
    iconf.check()
    assert len(iconf.config.constraint_violations) == 6
    assert 'ooasp_cv(lowerbound,2,"Lowerbound for {} is {} but has {} {}",(rack_frames,1,0,rack' in iconf.state.config.fb.asp_str()
    assert 'ooasp_cv(lowerbound,1,"Lowerbound for {} is {} but has {} {}",(rack_frames,1,0,rack' in iconf.state.config.fb.asp_str()
    assert 'ooasp_cv(lowerbound,3,"Lowerbound for {} is {} but has {} {}",(rack_frames,1,0,rack' in iconf.state.config.fb.asp_str()
    assert 'ooasp_cv(no_value,1,"Missing value for {}",(frame_position,))' in iconf.state.config.fb.asp_str()
    assert 'ooasp_cv(no_value,2,"Missing value for {}",(frame_position,))' in iconf.state.config.fb.asp_str()
    assert 'ooasp_cv(no_value,3,"Missing value for {}",(frame_position,))' in iconf.state.config.fb.asp_str()

def test_s_interactive_check_custom_cv():
    iconf = new_racks_iconf()
    iconf.check()
    assert len(iconf.config.constraint_violations) == 0
    iconf.new_object('rackSingle')
    iconf.check()
    found = iconf.extend_incrementally()
    iconf.select_found_configuration()
    iconf.new_object('frame')
    iconf.select_association('rack_frames',1,6)
    iconf.check()
    assert '(upperbound,1,"Upperbound for {} exceeded: {}",(rack_framesS,4,' in iconf.state.config.fb.asp_str()
    



def test_s_interactive_select():
    iconf = new_racks_iconf()
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
    iconf = new_racks_iconf()
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

    iconf = new_racks_iconf()




def test_normal_extend():
    iconf = new_racks_iconf()
    iconf.new_object('rackSingle')
    found = iconf.extend_incrementally()
    found_str = found.fb.asp_str()

    assert found
    assert iconf.domain_size == 5
    assert "ooasp_domain(rackSingle,1)." in found_str
    assert "ooasp_isa_leaf(rackSingle,1)." in found_str

def test_new_propagate():
    iconf = new_racks_iconf()
    iconf.new_object('rackSingle',propagate=True)
    conf_str = iconf.config.fb.asp_str()
    assert 'ooasp_domain(rackSingle,1).' in conf_str
    assert 'ooasp_domain(frame,2).'  in conf_str
    assert 'ooasp_domain(frame,3).'  in conf_str
    assert 'ooasp_domain(frame,4).'  in conf_str
    assert 'ooasp_domain(frame,5).'  in conf_str
    assert 'ooasp_associated(rack_framesS,1,2).'  in conf_str
    assert 'ooasp_associated(rack_framesS,1,3).'  in conf_str
    assert 'ooasp_associated(rack_framesS,1,4).'  in conf_str
    assert 'ooasp_associated(rack_framesS,1,5)'  in conf_str


def test_extend_propagate_symmetry():
    iconf = new_racks_iconf()
    # iconf.extend_domain(5,cls='object',propagate=True)
    iconf.extend_domain(1,cls='rackSingle')
    iconf.extend_domain(4,cls='frame')
    found = iconf.next_solution()
    assert found
    found = iconf.next_solution()
    assert found


    iconf = new_racks_iconf()
    iconf.extend_domain(4,cls='frame')
    iconf.extend_domain(1,cls='rackSingle')
    found = iconf.next_solution()
    assert found
    found = iconf.next_solution()
    assert found

def test_create_required_objects():
    iconf = new_racks_iconf()
    iconf.new_object('rackSingle')
    iconf.extend_domain(3,cls='frame')
    iconf.select_association('rack_frames',1,2)
    iconf.select_association('rack_frames',1,3)
    iconf.select_association('rack_frames',1,4)
    iconf._create_required_objects(1)
    config_str = iconf.config.fb.asp_str()
    assert "ooasp_domain(frame,5)." in config_str
    found = iconf.next_solution()
    assert found
    assert found.size == 5
    assert found.domain_size == 5

def test_create_all_required_objects():
    iconf = new_racks_iconf()
    iconf.new_object('rackSingle')
    iconf.new_object('frame')
    iconf._create_all_required_objects()
    config_str = iconf.config.fb.asp_str()
    assert "ooasp_domain(frame,5)." in config_str
    found = iconf.next_solution()
    assert found
    assert found.size == 5
    assert found.domain_size == 5

def test_custom_interactive_add_leaf_extend_browse():
    iconf = new_racks_iconf()

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
    iconf = new_racks_iconf()

    iconf.extend_domain(1,'rackSingle')
    iconf.select_object_class(1, 'rackDouble')
    ok = iconf.check()
    assert ok # Its ok because the rackDouble is ignored since it no external is grounded for user(ooasp_isa(1,rackDouble))

def test_add_remove_assoc():
    iconf = new_racks_iconf()
    
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
    iconf = new_racks_iconf()

    iconf.new_object('rackSingle')
    iconf.new_object('rackSingle')
    iconf.new_object('rackSingle')
    found = iconf.extend_incrementally()
    found.save_png(directory="./out/test")
