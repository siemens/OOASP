# Copyright (c) 2022 Siemens AG Oesterreich
# SPDX-License-Identifier: MIT

import pytest
from ooasp.kb import OOASPKnowledgeBase
import ooasp.settings as settings
settings.init('basic')
import pytest
from importlib import reload
@pytest.fixture(autouse=True)
def overwrite_settings():
    settings = reload(__import__("ooasp").settings)
    settings.init('basic')
    yield

def test_kb_create():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1","./examples/racks/kb.lp")
    assert racks_kb.name=="racks_v1"
    assert "ooasp_assoc(racks_v1,rack_frames,rack,1,1,frame,4,8)." in racks_kb.fb.asp_str()
    assert "ooasp_attribute(racks_v1,frame,frame_position,int)." in racks_kb.fb.asp_str()
    assert "ooasp_attribute_maxInclusive(racks_v1,frame,frame_position,8)." in racks_kb.fb.asp_str()
    assert "ooasp_class(racks_v1,object)." in racks_kb.fb.asp_str()
    assert "ooasp_class(racks_v1,rack)." in racks_kb.fb.asp_str()
    assert "ooasp_kb(racks_v1)." in racks_kb.fb.asp_str()
    assert "ooasp_subclass(racks_v1,moduleV,module)." in racks_kb.fb.asp_str()


def test_kb_create_wrong_name():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v2","./examples/racks/kb.lp")
    assert racks_kb.name=="racks_v2"
    assert "ooasp_class(racks_v2,object)." not in racks_kb.fb.asp_str()


def test_kb_is_leaf():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1","./examples/racks/kb.lp")
    assert racks_kb.is_leaf('frame')
    assert racks_kb.direct_subclasses('rack') == ['rackSingle','rackDouble']
    assert not racks_kb.is_leaf('rack')
    assert racks_kb.is_leaf('rackSingle')