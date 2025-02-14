
# -*- coding: UTF-8 -*-

from datetime import datetime


_DATETIME_FORMAT = "%Y%m%d%H%M%S%f"


class Time(datetime):
    def __new__(cls, time: datetime | str | int | None = None):
        if isinstance(time, Time):
            return time
        
        if isinstance(time, str) and len(time) == 14:
            time += "000000"
        
        if isinstance(time, str):
            lower_time = time.lower()
            if lower_time == "min":
                dt = datetime.min
            elif lower_time == "max":
                dt = datetime.max
            elif lower_time == "now":
                dt = datetime.now()
            else:
                dt = datetime.strptime(time, _DATETIME_FORMAT)
        elif isinstance(time, int):
            dt = datetime.fromtimestamp(time)
        elif isinstance(time, datetime):
            dt = time
        elif time is None:
            dt = datetime.now()
        else:
            raise ValueError(f"Invalid time: {time}")

        return super().__new__(
            cls,
            dt.year, dt.month, dt.day,
            dt.hour, dt.minute, dt.second, dt.microsecond,
            dt.tzinfo
        )

    def __str__(self):
        if self == datetime.min:
            return "min"
        elif self == datetime.max:
            return "max"
        return self.strftime(_DATETIME_FORMAT)

    def __repr__(self):
        return self.__str__()


Time.min = Time("min")
Time.max = Time("max")

