# -*- coding: UTF-8 -*-


from types import NoneType
from typing import Optional, Union
from typing import Iterable, Tuple, List, Set, Dict, Any
from typing import get_type_hints, get_origin, get_args

from enum import Enum
from dataclasses import dataclass, field, asdict, is_dataclass
from datetime import datetime
from contextlib import suppress
from pathlib import Path

from ..time import Time
from ..identifier import TestId, JobId, DutId
from ..profile import Profile
from ..test import Job

from .rule import RuleLevel, Rule, RuleViolation



def _ReportItem(item: Union["ReportItem", dict]) -> "ReportItem":
    """
    Helper function to ensure that the item is either a ReportSection or ReportEntry.
    """
    if isinstance(item, (ReportSection, ReportEntry)):
        return item
    with suppress(TypeError, ValueError):
        return ReportSection(**item)
    with suppress(TypeError, ValueError):
        return ReportEntry(**item)
    raise TypeError("items must contain only ReportSection or ReportEntry instances")


@dataclass
class ReportEntry:
    key             : str                   = ""
    name            : str                   = ""
    unit            : str                   = ""
    description     : str                   = ""
    style           : str                   = ""
    violations      : List[RuleViolation]   = field(default_factory=list)
    data            : Dict[str, Any]        = field(default_factory=dict)

    def __post_init__(self):
        self.key = str(self.key)
        self.name = str(self.name)
        self.unit = str(self.unit)
        self.description = str(self.description)
        self.style = str(self.style)
        self.violations = [
            violation
            if isinstance(violation, RuleViolation)
            else RuleViolation(**violation)
            for violation in self.violations
        ]
        self.data = {
            str(k): v
            for k, v in self.data.items()
        }


@dataclass
class ReportSection:
    name            : str
    items           : List["ReportItem"]    = field(default_factory=list)

    def __post_init__(self):
        self.name = str(self.name)
        self.items = [
            _ReportItem(item)
            for item in self.items
        ]


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


