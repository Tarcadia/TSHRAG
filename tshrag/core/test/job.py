
# -*- coding: UTF-8 -*-


from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..data import Id

from .load import Load
from .run import Run



class JobId(Id):
    pass



@dataclass
class Job(Run):
    id              : JobId
    test_id         : str
    load            : Load
    env             : Dict[str, str]        = field(default_factory=dict)
    args            : List[str]             = field(default_factory=list)
    pid             : Optional[int]         = None
    retcode         : Optional[int]         = None

    def __post_init__(self):
        super().__post_init__()
        self.id = JobId(self.id)
        if isinstance(self.load, dict):
            self.load = Load(**self.load)
