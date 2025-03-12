
# -*- coding: UTF-8 -*-


from dataclasses import dataclass, field
from typing import Any

from .id import Id
from .time import Time



class MetricId(str):

    SEPARATOR = "::"

    def __new__(cls, *keys):
        _keys = [Id(k) for k in keys]
        return str.__new__(cls, cls.SEPARATOR.join(_keys))
    
    def keys(self):
        return self.split(self.SEPARATOR)



@dataclass
class Metric:
    id              : MetricId
    name            : str                   = ""
    type            : str                   = ""
    description     : str                   = ""

    def __post_init__(self):
        self.id = MetricId(self.id)


@dataclass
class MetricEntry:
    time            : Time                  = field(default_factory=Time)
    value           : Any                   = None

    def __post_init__(self):
        self.time = Time(self.time)

