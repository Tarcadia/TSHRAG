# -*- coding: UTF-8 -*-

from datetime import datetime
from datetime import timedelta
from datetime import timezone

from tzlocal import get_localzone



class Time(datetime):

    UNIT_RATE = 1_000_000

    def __new__(cls, *t):
        if len(t) == 0:
            dt = datetime.now()
        elif len(t) > 1:
            dt = datetime(*t)
        elif isinstance(time:=t[0], Time):
            return time
        elif time:=t[0] is None:
            dt = datetime.now()
        elif isinstance(time:=t[0], datetime):
            dt = time
        elif isinstance(time:=t[0], timedelta):
            dt = datetime.now() + time
        elif isinstance(time:=t[0], (int, float)):
            dt = datetime.fromtimestamp(time / cls.UNIT_RATE, tz=timezone.utc)
        elif isinstance(time:=t[0], str) and time.lower() == "min":
            dt = datetime.min
        elif isinstance(time:=t[0], str) and time.lower() == "max":
            dt = datetime.max
        elif isinstance(time:=t[0], str) and time.lower() == "now":
            dt = datetime.now()
        elif isinstance(time:=t[0], str) and time.isdecimal():
            dt = datetime.fromtimestamp(int(time) / cls.UNIT_RATE, tz=timezone.utc)
        elif isinstance(time:=t[0], str):
            try:
                dt = datetime.fromisoformat(time)
            except ValueError:
                raise ValueError(f"Invalid ISO8601 format: {time}")
        else:
            raise ValueError(f"Invalid time: {t[0]}")

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=get_localzone())

        return super().__new__(
            cls,
            dt.year, dt.month, dt.day,
            dt.hour, dt.minute, dt.second, dt.microsecond,
            dt.tzinfo
        )

    def __int__(self):
        return int(self.timestamp() * self.UNIT_RATE)

    def __float__(self):
        return float(self.timestamp() * self.UNIT_RATE)

    def __str__(self):
        if self == Time.min:
            return "min"
        elif self == Time.max:
            return "max"
        return self.isoformat()

    def __repr__(self):
        return f"Time('{self}')"

    def __add__(self, value):
        if isinstance(value, (int, float)):
            return Time(int(self) + int(value))
        if isinstance(value, timedelta):
            return Time(datetime.__add__(self, value))
        return NotImplemented

    def __radd__(self, value):
        return self.__add__(value)


Time.min = Time("min")
Time.max = Time("max")


