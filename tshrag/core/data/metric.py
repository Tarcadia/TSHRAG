
# -*- coding: UTF-8 -*-


from enum import Enum
from dataclasses import dataclass, field
from typing import Any

from .time import Time



class MetricType(str, Enum):
    LOG             = "LOG"
    DATA            = "DATA"



@dataclass
class Metric:
    id              : str
    type            : MetricType
    description     : str                   = ""

    def __post_init__(self):
        self.id = self.id.lower()
        if isinstance(self.type, str):
            self.type = MetricType(self.type.upper())


@dataclass
class MetricEntry:
    time            : Time                  = field(default_factory=Time)

    def __post_init__(self):
        self.time = Time(self.time)


@dataclass
class MetricDataEntry(MetricEntry):
    value           : Any                   = None


@dataclass
class MetricLogEntry(MetricEntry):
    value           : str                   = ""
    unit            : str                   = ""

