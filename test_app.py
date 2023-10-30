from app import *

def test_get_height():
    assert get_height_from_sensor() >= 28
    assert get_height_from_sensor() <= 45

def test_set_height():
    assert set_height(35) == 35 
    assert set_height(36) == 36