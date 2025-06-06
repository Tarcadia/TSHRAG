# -*- coding: UTF-8 -*-


from types import NoneType
from typing import Optional, Union
from typing import Iterable, Tuple, List, Set, Dict, Any
from typing import get_type_hints, get_origin, get_args

from enum import Enum
from dataclasses import dataclass



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


