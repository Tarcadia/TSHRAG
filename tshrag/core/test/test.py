
# -*- coding: UTF-8 -*-


from dataclasses import dataclass, field
from typing import Dict, List

from .run import Run
from .job import Job



@dataclass
class Test(Run):
    id              : str
    dut             : Dict[str, str]        = field(default_factory=dict)
    jobs            : List[Job]             = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        self.id = self.id.lower()
        if isinstance(self.jobs, list):
            self.jobs = [
                Job(**job) if isinstance(job, dict) else job
                for job in self.jobs
            ]
