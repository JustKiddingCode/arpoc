import datetime
from typing import Any

from . import _lib

import arpoc.utils

class EnvAttrTime(_lib.EnvironmentAttribute):
    """ Returns the current time in HH:MM:SS format """

    target = "time"

    @staticmethod
    def run() -> Any:
        now = arpoc.utils.now_object()
        return "{:02d}:{:02d}:{:02d}".format(now.hour, now.minute, now.second)


class EnvAttrDateTime(_lib.EnvironmentAttribute):
    """ Returns the current time in YYYY-MM-DD HH:MM:SS format """

    target = "datetime"

    @staticmethod
    def run() -> Any:
        now = arpoc.utils.now_object()
        return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(now.year, now.month, now.day,
                                          now.hour, now.minute, now.second)


class EnvAttrTimeHour(_lib.EnvironmentAttribute):
    """ Returns the current hours of the clock """

    target = "time_hour"

    @staticmethod
    def run() -> Any:
        now = arpoc.utils.now_object()
        return now.hour


class EnvAttrTimeMinute(_lib.EnvironmentAttribute):
    """ Returns the current minute of the clock """

    target = "time_minute"

    @staticmethod
    def run() -> Any:
        now = arpoc.utils.now_object()
        return now.minute


class EnvAttrTimeSecond(_lib.EnvironmentAttribute):
    """ Returns the current second of the clock """

    target = "time_second"

    @staticmethod
    def run() -> Any:
        now = arpoc.utils.now_object()
        return now.second
