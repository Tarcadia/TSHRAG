
# -*- coding: UTF-8 -*-


from dataclasses import dataclass, field
from typing import Dict, List

from ..data import Id

from ..profile import Profile
from .run import Run
from .job import Job



class TestId(Id):
    pass



@dataclass
class Test(Run):
    id              : TestId
    profile         : Profile
    dut             : Dict[str, str]        = field(default_factory=dict)
    jobs            : List[Job]             = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        self.id = TestId(self.id)
        if isinstance(self.profile, dict):
            self.profile = Profile(**self.profile)
        if isinstance(self.jobs, list):
            self.jobs = [
                Job(**job) if isinstance(job, dict) else job
                for job in self.jobs
            ]
