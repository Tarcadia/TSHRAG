
# -*- coding: UTF-8 -*-


from typing import Optional
from typing import Tuple, List, Set, Dict, Any
from dataclasses import dataclass, field
from pathlib import Path

from ..time import Time
from ..identifier import TestId, JobId, DutId
from ..metric import MetricDB
from ..profile import Profile

from .run import Run
from .job import Job



@dataclass
class Test(Run):
    id              : TestId
    profile         : Optional[Profile]     = None
    duration        : int                   = -1
    machine         : List[DutId]           = field(default_factory=list)
    device          : List[DutId]           = field(default_factory=list)
    env             : Dict[str, str]        = field(default_factory=dict)
    jobs            : List[JobId]           = field(default_factory=list)
    mdb             : Optional[Path]        = None

    def __post_init__(self):
        super().__post_init__()
        self.id = TestId(self.id)
        if isinstance(self.profile, dict):
            self.profile = Profile(**self.profile)
        self.duration = int(self.duration)
        self.machine = list({DutId(m) for m in self.machine})
        self.device = list({DutId(d) for d in self.device})
        self.env = {
            str(k): str(v)
            for k, v in self.env.items()
        }
        self.jobs = [
            JobId(id)
            for id in self.jobs
        ]
        self.mdb = self.mdb and Path(self.mdb)


    def get_mdb(self) -> MetricDB:
        return self.mdb and MetricDB(self.mdb)

