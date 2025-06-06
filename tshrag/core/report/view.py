# -*- coding: UTF-8 -*-


from types import NoneType
from typing import Optional, Union
from typing import Iterable, Tuple, List, Set, Dict, Any
from typing import get_type_hints, get_origin, get_args

from dataclasses import dataclass, field

from ..metric import MetricKey



def _ViewItem(item: Union["ViewItem", dict]) -> "ViewItem":
    """
    Helper function to ensure that the item is either a ViewSection or ViewEntry.
    """
    if isinstance(item, (ViewSection, ViewEntry)):
        return item
    else:
        _item = None
        try:
            _item = ViewEntry(**item)
        except TypeError:
            pass
        try:
            _item = ViewSection(**item)
        except TypeError:
            pass
        if _item is None:
            raise TypeError("items must contain only ViewSection or ViewEntry instances")
        return _item


@dataclass
class ViewEntry:
    key             : str                   = ""
    name            : str                   = ""
    description     : str                   = ""
    style           : str                   = ""

    def __post_init__(self):
        self.key = str(self.key)
        self.name = str(self.name)
        self.description = str(self.description)
        self.style = str(self.style)


@dataclass
class ViewSection:
    name            : str                   = ""
    items           : List["ViewItem"]      = field(default_factory=list)

    def __post_init__(self):
        self.name = str(self.name)
        if not isinstance(self.items, list):
            raise TypeError("items must be a list of ViewSection or ViewEntry instances")
        self.items = [_ViewItem(item) for item in self.items]


ViewItem = Union[ViewSection, ViewEntry]


@dataclass
class View:
    sections        : List[ViewSection]     = field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.sections, list):
            raise TypeError("sections must be a list of ViewSection instances")
        self.sections = [
            section
            if isinstance(section, ViewSection)
            else ViewSection(**section)
            for section in self.sections
        ]


