
# -*- coding: UTF-8 -*-


from dataclasses import dataclass, field
from typing import Any

from .id import Id, sub_ids
from .time import Time



class MetricId(str):

    SEPARATOR = "::"

    def __new__(cls, *keys):
        _keys = [id for k in keys for id in sub_ids(str(k))]
        return str.__new__(cls, cls.SEPARATOR.join(_keys))
    
    def keys(self):
        return self.split(self.SEPARATOR)



class MetricIdPattern(MetricId):
    def __new__(cls, *keys):
        if not keys:
            keys = ["*"]
        _keys = [id for k in keys for id in sub_ids(str(k), id_chars=(Id.ID_CHARS + "*"))]
        return str.__new__(cls, cls.SEPARATOR.join(_keys))



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

