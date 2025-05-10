
# -*- coding: UTF-8 -*-


from typing import Any, List
from dataclasses import dataclass, field

from ..identifier import Identifier, split_identifier
from ..time import Time



class MetricKey(str):

    SEPARATOR = "."

    def __new__(cls, *keys):
        _subkeys = [id for k in keys for id in split_identifier(str(k)) if id]
        return str.__new__(cls, cls.SEPARATOR.join(_subkeys))
    
    def subkeys(self) -> List[str]:
        return self.split(self.SEPARATOR)


@dataclass
class MetricInfo:
    key             : MetricKey
    name            : str                   = ""
    description     : str                   = ""

    def __post_init__(self):
        self.key = MetricKey(self.key)
        self.name = str(self.name)
        self.description = str(self.description)


@dataclass
class MetricEntry:
    time            : Time                  = field(default_factory=Time)
    duration        : int                   = 0.0
    value           : Any                   = None

    def __post_init__(self):
        self.time = Time(self.time)
        if self.duration < 0:
            raise ValueError(f"Negative duration: {self.duration}")
        self.duration = int(self.duration)

