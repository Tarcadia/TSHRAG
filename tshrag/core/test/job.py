
# -*- coding: UTF-8 -*-


from typing import Optional
from typing import Tuple, List, Set, Dict, Any
from pathlib import Path
from dataclasses import dataclass, field

from ..time import Time
from ..identifier import TestId, JobId, DutId
from .run import Run



@dataclass
class Job(Run):
    id              : JobId
    machine         : Optional[str]         = None
    device          : Set[str]              = field(default_factory=set)
    args            : List[str]             = field(default_factory=list)
    cwd             : str                   = ""
    env             : Dict[str, str]        = field(default_factory=dict)
    pid             : Optional[int]         = None
    retcode         : Optional[int]         = None

    def __post_init__(self):
        super().__post_init__()
        self.id = JobId(self.id)
        self.machine = self.machine and str(self.machine)
        self.device = {str(d) for d in self.device}
        self.args = [str(arg) for arg in self.args]
        self.cwd = self.cwd.as_posix() if isinstance(self.cwd, Path) else str(self.cwd)
        self.env = {str(k): str(v) for k, v in self.env.items()}
        self.pid = self.pid and int(self.pid)
        self.retcode = self.retcode and int(self.retcode)


