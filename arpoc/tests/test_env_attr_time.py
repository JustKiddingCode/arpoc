
from unittest.mock import patch

import datetime
import arpoc.utils

from arpoc.plugins.env_attr_time import *
time_object = datetime.datetime.fromisoformat("2000-07-08 01:02:03")

def test_datetime_object():
    diff = arpoc.utils.now_object().timestamp() - datetime.datetime.now().timestamp()
    assert diff <= 0.5

@patch('arpoc.utils.now_object',return_value=time_object)
def test_time(mock):
    assert EnvAttrTime.run() == "01:02:03"
    assert EnvAttrDateTime.run() == "2000-07-08 01:02:03"
    assert EnvAttrTimeHour.run() == 1
    assert EnvAttrTimeMinute.run() == 2
    assert EnvAttrTimeSecond.run() == 3



time_object = datetime.datetime.fromisoformat("2000-07-08 17:02:03")
@patch('arpoc.utils.now_object',return_value=time_object)
def test_time_big_hour(mock):
    assert EnvAttrTimeHour.run() == 17

