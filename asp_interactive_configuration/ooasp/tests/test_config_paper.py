# Copyright (c) 2022 Siemens AG Oesterreich
# SPDX-License-Identifier: MIT

from ooasp.kb import OOASPKnowledgeBase
from ooasp.config import OOASPConfiguration

import pytest
from importlib import reload
@pytest.fixture(autouse=True)
def overwrite_settings():
    settings = reload(__import__("ooasp").settings)
    settings.init('paper')
    yield

def test_s_config_create():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1","./examples/racks/kb_simple.lp")
    config = OOASPConfiguration("i1",racks_kb)
    config.fb.add(config.UNIFIERS.Leaf(class_name='frame',object_id=1))
    assert "ooasp_isa_leaf(frame,1)." in config.fb.asp_str()


def test_s_config_add_value():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1","./examples/racks/kb_simple.lp")
    config = OOASPConfiguration("i1",racks_kb)
    config.add_value(1,'frame_position',1)
    fact =  "ooasp_attr_value(frame_position,1,1)"
    assert fact in config.fb.asp_str()
    removed_l = config.remove_value(1,'frame_position')
    assert len(removed_l)==1
    removed = removed_l[0]
    assert str(removed) == fact
    assert fact not in config.fb.asp_str()


def test_s_config_add_leaf():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1","./examples/racks/kb_simple.lp")
    config = OOASPConfiguration("i1",racks_kb)
    config.add_leaf(1,'frame')
    fact = "ooasp_isa_leaf(frame,1)"
    assert fact in config.fb.asp_str()
    removed_l = config.remove_leaf(1)
    assert len(removed_l)==1
    removed = removed_l[0]
    assert str(removed) == fact
    assert fact not in config.fb.asp_str()

def test_s_config_add_association():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1","./examples/racks/kb_simple.lp")
    config = OOASPConfiguration("i1",racks_kb)
    config.add_association('rack_frames',1,2)
    fact = 'ooasp_associated(rack_frames,1,2)'
    assert fact in config.fb.asp_str()
    removed_l = config.remove_association("rack_frames",1,2)
    assert len(removed_l)==1
    removed = removed_l[0]
    assert str(removed) == fact
    assert fact not in config.fb.asp_str()



def test_s_config_size():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1","./examples/racks/kb_simple.lp")
    config = OOASPConfiguration("i1",racks_kb)
    config.add_domain('class',1)
    config.add_domain('class',2)
    config.add_domain('class',3)
    assert config.domain_size==3
