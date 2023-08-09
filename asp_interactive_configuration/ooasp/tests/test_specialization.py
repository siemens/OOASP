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

def test_specialization():
    iconf = new_racks_iconf()

    iconf.extend_domain(5)
    iconf.select_object_class(1, 'rackSingle')
    iconf.select_object_class(2, 'frame')
    iconf.select_object_class(3, 'frame')
    iconf.select_object_class(4, 'frame')
    iconf.select_object_class(5, 'frame')
    iconf.select_association('rack_frames',1,2)
    iconf.select_association('rack_frames',1,3)
    iconf.select_association('rack_frames',1,4)
    iconf.select_association('rack_frames',1,5)
    iconf.check()
    # Only the missing values
    assert len(iconf.config.constraint_violations) == 4

def test_specialization_extend():
    iconf = new_racks_iconf()
    iconf.new_object('rackSingle')
    found = iconf.extend_incrementally()    
    assert found
    assert found.size == 5

    iconf = new_racks_iconf()
    iconf.new_object('rackDouble')
    found = iconf.extend_incrementally()    
    assert found
    assert found.size == 9

def test_s_interactive_extend_incrementally_overshooting_rack_specialization():
    iconf = new_racks_iconf()
    iconf.new_object('rackSingle')
    found = iconf.extend_incrementally(overshoot=True)
    assert found
    print(found)
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
    print(found)
    assert iconf.domain_size == 10


def test_specialization_cautious():
    iconf = new_racks_iconf()
    iconf.new_object('rackDouble')
    iconf.new_object('frame')
    cautious = iconf._get_cautious()
    print(cautious)
    iconf.extend_domain(3)
    cautious = iconf._get_cautious()
    print(cautious)