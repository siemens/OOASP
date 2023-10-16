# Copyright (c) 2022 Siemens AG Oesterreich
# SPDX-License-Identifier: MIT

from ooasp.interactive import InteractiveConfigurator
from ooasp.kb import OOASPKnowledgeBase
from ooasp import settings
from ooasp.tests.utils import new_metrof_iconf

import pytest
from importlib import reload

def test_metro_next():
    """ test element constraints """
    iconf = new_metrof_iconf()
    iconf.new_object("wagon")
    found = iconf.next_solution()
    assert found
    assert "ooasp_attr_value(nr_seats,1,0)." in str(found)
    assert "ooasp_attr_value(standing_room,1,0)." in str(found)
    assert "ooasp_attr_value(nr_passengers,1,0)." in str(found)
    found = iconf.next_solution()
    assert not found

def test_metro_options():
    """ test element constraints """
    iconf = new_metrof_iconf()
    iconf.new_object("wagon")
    iconf.select_fvalue(1,"standing_room",1)
    brave = iconf.get_options()
    opts = iconf._brave_config_as_options()
    opts_set = set()
    for o in opts[1]:
        if o['fun_name']=='select_value' and o['args'][1]=='standing_room':
            opts_set.add(o['args'][2])
    print(opts_set)
    assert len(opts_set)==20 #All possible values as options
    iconf.extend_incrementally()
    iconf.select_found_configuration()
    print(iconf.config)
    iconf.select_fvalue(1,"nr_passengers",0)
    brave = iconf.get_options()
    assert brave is None
    opts = iconf._brave_config_as_options()
    fun_names = [f['fun_name'] for f in opts[1]]
    assert 'remove_value' in fun_names
    assert 'remove_object_class' in fun_names
    assert 'remove_association' in fun_names
    
def test_metro_cv_wagon_constraints():
    """ test element constraints """
    iconf = new_metrof_iconf()
    iconf.new_object("wagon")
    iconf.check()
    assert len(iconf.config.constraint_violations) ==3
    iconf.select_value(1,"nr_passengers",10)
    iconf.select_value(1,"nr_seats",10)
    iconf.select_value(1,"standing_room",0)
    iconf.check()
    assert len(iconf.config.constraint_violations) ==1
    assert  "Number of seats should be {}" in str(iconf.config.constraint_violations)
    

def test_metro_cv_wagon_wrong_nr_pass():
    """ test element constraints """
    iconf = new_metrof_iconf()
    iconf.new_object("wagon")
    iconf.check()
    assert len(iconf.config.constraint_violations) ==3
    iconf.select_value(1,"nr_passengers",15)
    iconf.select_value(1,"nr_seats",10)
    iconf.select_value(1,"standing_room",0)
    iconf.check()
    assert len(iconf.config.constraint_violations) ==2
    assert not "Number of passengers calculated" in str(iconf.config.constraint_violations)

def test_metro_cv_handrail_required():
    """ test element constraints """
    iconf = new_metrof_iconf()
    iconf.new_object("wagon")
    iconf.select_value(1,"standing_room",10)
    iconf.check()
    assert len(iconf.config.constraint_violations) ==3
    assert "Handrail required" in str(iconf.config.constraint_violations)
    iconf.new_object("handrail")
    iconf.select_association('wagon_handrail',1,2)
    iconf.check()
    assert len(iconf.config.constraint_violations) ==2
    assert not "Handrail required" in str(iconf.config.constraint_violations)


def test_metro_multi_wagon():
    """ test element constraints """
    iconf = new_metrof_iconf()
    iconf.new_object("wagon")
    iconf.new_object("wagon")
    iconf.check()
    assert len(iconf.config.constraint_violations) ==7
    assert "Only one wagon allowed" in str(iconf.config.constraint_violations)
    opt = iconf._get_options()
    assert opt == None
    brave_dic = iconf._brave_config_as_options()
    assert brave_dic[1][0]['fun_name']=='remove_object_class'

def test_metro_cv_wagon():
    """ test element constraints """
    iconf = new_metrof_iconf()
    iconf.new_object("wagon")
    iconf.extend_domain(5)
    for i in range(20):
        c = iconf.next_solution()
        assert c
        attr = c.UNIFIERS.AttributeValue
        nr_p = list(c.fb.query(attr).where(attr.attr_name=='nr_passengers').select(attr.attr_value).all())[0].symbol.number
        nr_s = list(c.fb.query(attr).where(attr.attr_name=='nr_seats').select(attr.attr_value).all())[0].symbol.number
        sr = list(c.fb.query(attr).where(attr.attr_name=='standing_room').select(attr.attr_value).all())[0].symbol.number
        assert nr_s >=0
        assert nr_s <=20
        assert sr >= 0
        assert sr <=20
        assert nr_p == nr_s + sr
        

def test_metro_cv_seat_color():
    """ test element constraints """
    iconf = new_metrof_iconf()
    iconf.new_object("wagon")
    iconf.new_object("seat")
    iconf.new_object("seat")
    iconf.select_value(1,"nr_passengers",2)
    iconf.select_value(1,"nr_seats",2)
    iconf.select_value(1,"standing_room",0)
    iconf.select_value(2,"seat_type",'special')
    iconf.select_value(2,"seat_color",'blue')
    iconf.select_value(3,"seat_type",'special')
    iconf.select_value(3,"seat_color",'red')
    iconf.select_association('wagon_seats',1,2)
    iconf.select_association('wagon_seats',1,3)
    iconf.check()
    assert len(iconf.config.constraint_violations) ==1
    assert  "Sepecial seats should be red" in str(iconf.config.constraint_violations)
    iconf.select_value(2,"seat_type",'premium')
    iconf.select_value(2,"seat_color",'blue')
    iconf.select_value(3,"seat_type",'premium')
    iconf.select_value(3,"seat_color",'red')
    iconf.check()
    assert len(iconf.config.constraint_violations) ==1
    assert  "All colors must be equal" in str(iconf.config.constraint_violations)
    iconf.select_value(2,"seat_type",'premium')
    iconf.select_value(2,"seat_color",'blue')
    iconf.select_value(3,"seat_type",'standard')
    iconf.select_value(3,"seat_color",'blue')
    iconf.check()
    assert len(iconf.config.constraint_violations) ==1
    assert  "All seat types must be equal" in str(iconf.config.constraint_violations)
    iconf.select_value(2,"seat_type",'premium')
    iconf.select_value(2,"seat_color",'blue')
    iconf.select_value(3,"seat_type",'premium')
    iconf.select_value(3,"seat_color",'blue')
    iconf.check()
    assert len(iconf.config.constraint_violations) ==0