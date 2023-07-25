# Copyright (c) 2022 Siemens AG Oesterreich
# SPDX-License-Identifier: MIT

import pytest
from ooasp.kb import OOASPKnowledgeBase
import ooasp.settings as settings
settings.init('defined')
import pytest
from importlib import reload
@pytest.fixture(autouse=True)
def overwrite_settings():
    settings = reload(__import__("ooasp").settings)
    settings.init('defined')
    yield

def test_kb_create():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    assert racks_kb.name=="racks_v1"
    assert "ooasp_assoc(rack_frames,rack,1,1,frame,4,8)." in racks_kb.fb.asp_str()
    assert "ooasp_attr(frame,frame_position,int)." in racks_kb.fb.asp_str()
    assert "ooasp_attr_maxInclusive(frame,frame_position,8)." in racks_kb.fb.asp_str()
    assert "ooasp_class(object)." in racks_kb.fb.asp_str()
    assert "ooasp_class(rack)." in racks_kb.fb.asp_str()
    assert "ooasp_subclass(moduleV,module)." in racks_kb.fb.asp_str()


def test_kb_create_wrong_name():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v2",settings.racks_example_kb)
    assert racks_kb.name=="racks_v2"
    assert "ooasp_class(racks_v2,object)." not in racks_kb.fb.asp_str()


def test_kb_is_leaf():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    assert racks_kb.is_leaf('frame')
    assert racks_kb.direct_subclasses('rack') == ['rackSingle','rackDouble']
    assert not racks_kb.is_leaf('rack')
    assert racks_kb.is_leaf('rackSingle')

def test_kb_superclasses():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    assert racks_kb.direct_superclasses('moduleI') == ['module']
    sub =  racks_kb.direct_subclasses('module')
    assert 'moduleI' in sub
    assert 'moduleII' in sub
    assert 'moduleIII' in sub
    assert 'moduleIV' in sub
    assert 'moduleV' in sub
    assert racks_kb.direct_superclasses('frame') == ['object']

def test_kb_assoc():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    assoc =  racks_kb.associations('module')
    assoc1 =  racks_kb.associations('moduleI')
    assert ('frame_modules', 'frame', 1, 1) in assoc
    assert ('element_modules', 'element', 0, 1) in assoc
    assert assoc == assoc1