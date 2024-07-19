# Copyright (c) 2022 Siemens AG Oesterreich
# SPDX-License-Identifier: MIT

from ooasp.tests.utils import new_iconf


def test_racks_constraints_element():
    """ test element constraints """
    iconf = new_iconf()
    iconf.new_object("elementA")
    iconf.check()
    assert len(iconf.config.constraint_violations) == 1
    assert "lowerbound" in str(iconf.config.constraint_violations)
    assert '(element_modules1,1,0,module' in str(iconf.config.constraint_violations)


def test_racks_constraints_moduleI():
    """ test module constraints """
    iconf = new_iconf()
    iconf.new_object("moduleI")
    iconf.check()
    assert len(iconf.config.constraint_violations) == 2
    assert "lowerbound" in str(iconf.config.constraint_violations)
    assert "(element_modules1,1,0,elementA" in str(iconf.config.constraint_violations)


def test_racks_constraints_moduleV():
    """ the moduleV constraints """
    iconf = new_iconf()
    iconf.new_object("moduleV")
    iconf.check()
    assert len(iconf.config.constraint_violations) == 1
    assert "lowerbound" in str(iconf.config.constraint_violations)


def test_racks_constraints_frame():
    """ test frame constraints """
    iconf = new_iconf()
    iconf.new_object("frame")
    iconf.check()
    assert len(iconf.config.constraint_violations) == 2
    assert "no_value" in str(iconf.config.constraint_violations)
    assert "lowerbound" in str(iconf.config.constraint_violations)


def test_racks_constraints_rack():
    """ test rack constraints """
    iconf = new_iconf()
    iconf.new_object("rackDouble")
    iconf.check()
    assert len(iconf.config.constraint_violations) == 1
    assert "lowerbound" in str(iconf.config.constraint_violations)
    assert "rack_framesD,8,0,frame" in str(iconf.config.constraint_violations)
    for i in range(7):
        f_id = iconf.new_object("frame")
        iconf.select_value(f_id, 'frame_position', f_id-1)
        iconf.select_association("rack_frames", 1, f_id)

    iconf.check()
    assert len(iconf.config.constraint_violations) == 1
    assert "lowerbound" in str(iconf.config.constraint_violations)
    assert "rack_framesD,8,7,frame" in str(iconf.config.constraint_violations)


def test_racks_constraints_frame_position():
    """ test assoc constraints """
    iconf = new_iconf()
    iconf.new_object("frame")
    iconf.new_object("rackSingle")
    iconf.select_association('rack_frames', 2, 1)
    iconf.select_value(1, 'frame_position', 5)
    iconf.check()
    assert "frame_must_be_within_range" in str(iconf.config.constraint_violations)


def test_racks_constraints_associations():
    """ test assoc constraints """
    iconf = new_iconf()
    iconf.new_object("moduleV")
    iconf.new_object("elementA")
    iconf.select_association("element_modules", 2, 1)
    iconf.check()
    config_str = iconf.config.fb.asp_str()
    assert "associated(element_modules,2,1)" in config_str

    assert len(iconf.config.constraint_violations) == 2
    assert "element_modules1,1,0,moduleI" in str(iconf.config.constraint_violations)

    iconf = new_iconf()
    iconf.new_object("elementA")
    iconf.new_object("moduleV")
    iconf.select_association("element_modules", 1, 2)
    iconf.check()
    assert len(iconf.config.constraint_violations) == 2
    assert "element_modules1,1,0,moduleI" in str(iconf.config.constraint_violations)


def test_racks_constraints_moduleII_requires_moduleV():
    """ test moduleII requires moduleV constraint """
    iconf = new_iconf()
    iconf.new_object("frame")
    iconf.new_object("moduleII")
    iconf.new_object("moduleV")

    iconf.select_association("frame_modules", 1, 2)
    iconf.check()

    assert len(iconf.config.constraint_violations) == 5
    assert "moduleII_requires_moduleV" in str(iconf.config.constraint_violations)

    iconf.select_association("frame_modules", 1, 3)
    iconf.check()

    assert len(iconf.config.constraint_violations) == 3
    assert "moduleII_requires_moduleV" not in str(iconf.config.constraint_violations)

    iconf = new_iconf()
    iconf.new_object("frame")
    iconf.new_object("moduleV")
    iconf.new_object("moduleII")

    iconf.select_association("frame_modules", 1, 3)
    iconf.check()

    assert len(iconf.config.constraint_violations) == 5
    assert "moduleII_requires_moduleV" in str(iconf.config.constraint_violations)

    iconf.select_association("frame_modules", 1, 2)
    iconf.check()

    assert len(iconf.config.constraint_violations) == 3
    assert "moduleII_requires_moduleV" not in str(iconf.config.constraint_violations)


def test_racks_unique_constraint():
    """ test assoc constraints """
    iconf = new_iconf()
    iconf.new_object("rack")
    iconf.new_object("frame")
    iconf.new_object("frame")
    iconf.select_association("rack_frames", 1, 2)
    iconf.select_association("rack_frames", 1, 3)
    iconf.select_value(2, 'frame_position', 1)
    iconf.select_value(3, 'frame_position', 1)
    iconf.check()
    assert 'unique_attr,3,"Attribute {} must be unique among all {}s associated by {} to {}",(frame_position,frame,rack_frames,1' in str(
        iconf.config.constraint_violations)
    assert 'unique_attr,2,"Attribute {} must be unique among all {}s associated by {} to {}",(frame_position,frame,rack_frames,1' in str(
        iconf.config.constraint_violations)

    iconf = new_iconf()
    iconf.new_object("frame")
    iconf.new_object("frame")
    iconf.new_object("rack")
    iconf.select_association("rack_frames", 3, 1)
    iconf.select_association("rack_frames", 3, 2)
    iconf.select_value(1, 'frame_position', 1)
    iconf.select_value(2, 'frame_position', 1)
    iconf.check()
    assert 'ooasp_cv(unique_attr,1,"Attribute {} must be unique among all {}s associated by {} to {}",(frame_position,frame,rack_frames,3' in str(
        iconf.config.constraint_violations)
    assert 'ooasp_cv(unique_attr,2,"Attribute {} must be unique among all {}s associated by {} to {}",(frame_position,frame,rack_frames,3' in str(
        iconf.config.constraint_violations)


def test_solve_elements():
    """ solve one instance of each element type"""
    element_configuration_size = {"elementA": 7, "elementB": 9, "elementC": 9, "elementD": 10}
    for element_type in element_configuration_size.keys():
        iconf = new_iconf()
        iconf.new_object(element_type)
        config = iconf.extend_incrementally()
        assert len(config.constraint_violations) == 0
        assert config.domain_size == element_configuration_size[element_type]
