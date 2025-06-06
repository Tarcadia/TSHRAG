# -*- coding: UTF-8 -*-


from types import NoneType
from typing import Optional, Union
from typing import Iterable, Tuple, List, Set, Dict, Any
from typing import get_type_hints, get_origin, get_args

from enum import Enum
from dataclasses import dataclass, field, asdict, is_dataclass
from datetime import datetime
from pathlib import Path

from ..time import Time
from ..identifier import TestId, JobId, DutId
from ..profile import Profile
from ..test import Job



def _ReportItem(item: Union["ReportItem", dict]) -> "ReportItem":
    """
    Helper function to ensure that the item is either a ReportSection or ReportEntry.
    """
    if isinstance(item, (ReportSection, ReportEntry)):
        return item
    else:
        _item = None
        try:
            _item = ReportEntry(**item)
        except TypeError:
            pass
        try:
            _item = ReportSection(**item)
        except TypeError:
            pass
        if _item is None:
            raise TypeError("items must contain only ReportSection or ReportEntry instances")
        return _item


@dataclass
class ReportEntry:
    key             : str                   = ""
    name            : str                   = ""
    description     : str                   = ""
    style           : str                   = ""
    violations      : list                  = field(default_factory=list)
    data            : dict                  = field(default_factory=dict)

    def __post_init__(self):
        self.key = str(self.key)
        self.name = str(self.name)
        self.description = str(self.description)
        self.style = str(self.style)
        if not isinstance(self.violations, list):
            raise TypeError("violations must be a list")
        if not isinstance(self.data, dict):
            raise TypeError("data must be a dict")


@dataclass
class ReportSection:
    name            : str
    items           : List["ReportItem"]    = field(default_factory=list)

    def __post_init__(self):
        self.name = str(self.name)
        if not isinstance(self.items, list):
            raise TypeError("items must be a list of ReportSection or ReportEntry instances")
        self.items = [_ReportItem(item) for item in self.items]


ReportItem = Union[ReportSection, ReportEntry]


@dataclass
class Report:
    id              : TestId
    profile         : Optional[Profile]     = None
    start_time      : Time                  = Time.min
    end_time        : Time                  = Time.max
    machine         : List[DutId]           = field(default_factory=list)
    device          : List[DutId]           = field(default_factory=list)
    env             : Dict[str, str]        = field(default_factory=dict)
    jobs            : List[Job]             = field(default_factory=list)
    sections        : List[ReportSection]   = field(default_factory=list)


    def __post_init__(self):
        self.id = TestId(self.id)
        if not isinstance(self.profile, Profile):
            self.profile = Profile(**self.profile)
        if not isinstance(self.start_time, Time):
            self.start_time = Time(self.start_time)
        if not isinstance(self.end_time, Time):
            self.end_time = Time(self.end_time)
        self.machine = list({DutId(m) for m in self.machine})
        self.device = list({DutId(d) for d in self.device})
        self.env = {
            str(k): str(v)
            for k, v in self.env.items()
        }
        self.jobs = [
            job
            if isinstance(job, Job)
            else Job(**job)
            for job in self.jobs
        ]
        self.sections = [
            section
            if isinstance(section, ReportSection)
            else ReportSection(**section)
            for section in self.sections
        ]


