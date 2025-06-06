# -*- coding: UTF-8 -*-


from types import NoneType
from typing import Optional, Union
from typing import Iterable, Tuple, List, Set, Dict, Any
from typing import get_type_hints, get_origin, get_args

from dataclasses import dataclass, field
from contextlib import suppress

from .rule import RuleLevel, Rule, RuleViolation




def _ViewItem(item: Union["ViewItem", dict]) -> "ViewItem":
    """
    Helper function to ensure that the item is either a ViewSection or ViewEntry.
    """
    if isinstance(item, (ViewSection, ViewEntry)):
        return item
    with suppress(TypeError, ValueError):
        return ViewSection(**item)
    with suppress(TypeError, ValueError):
        return ViewEntry(**item)
    raise TypeError("items must contain only ViewSection or ViewEntry instances")


@dataclass
class ViewEntry:
    key             : str                   = ""
    name            : str                   = ""
    unit            : str                   = ""
    description     : str                   = ""
    style           : str                   = ""
    statistics      : List[str]             = field(default_factory=list)
    rules           : List[Rule]            = field(default_factory=list)

    def __post_init__(self):
        self.key = str(self.key)
        self.name = str(self.name)
        self.unit = str(self.unit)
        self.description = str(self.description)
        self.style = str(self.style)
        self.statistics = [
            str(statistic)
            for statistic in self.statistics
        ]
        self.rules = [
            rule
            if isinstance(rule, Rule)
            else Rule(**rule)
            for rule in self.rules
        ]


@dataclass
class ViewSection:
    name            : str                   = ""
    items           : List["ViewItem"]      = field(default_factory=list)

    def __post_init__(self):
        self.name = str(self.name)
        self.items = [
            _ViewItem(item)
            for item in self.items
        ]


ViewItem = Union[ViewSection, ViewEntry]


@dataclass
class View:
    sections        : List[ViewSection]     = field(default_factory=list)

    def __post_init__(self):
        self.sections = [
            section
            if isinstance(section, ViewSection)
            else ViewSection(**section)
            for section in self.sections
        ]


