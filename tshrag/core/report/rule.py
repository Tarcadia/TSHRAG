# -*- coding: UTF-8 -*-


from types import NoneType
from typing import Optional, Union
from typing import Iterable, Tuple, List, Set, Dict, Any
from typing import get_type_hints, get_origin, get_args

from enum import Enum
from dataclasses import dataclass, field

from ..time import Time



class RuleLevel(str, Enum):
    """
    Enum for rule levels.
    """
    WARNING         = "WARNING"
    ERROR           = "ERROR"
    CRITICAL        = "CRITICAL"



@dataclass
class Rule:
    description     : str                   = ""
    condition       : str                   = ""
    level           : RuleLevel             = RuleLevel.WARNING

    def __post_init__(self):
        self.description = str(self.description)
        self.condition = str(self.condition)
        if not isinstance(self.level, RuleLevel):
            self.level = RuleLevel(self.level.upper())


@dataclass
class RuleViolation(Rule):
    key             : str                   = ""
    statistic       : str                   = ""
    when            : List[Time]            = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        self.key = str(self.key)
        self.statistic = str(self.statistic)
        self.when = [
            time
            if isinstance(time, Time)
            else Time(time)
            for time in self.when
        ]


