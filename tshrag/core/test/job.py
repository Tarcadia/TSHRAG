
# -*- coding: UTF-8 -*-


from typing import Union, Optional, Generic, TypeVar
from typing import Iterable, Iterator, AsyncIterator
from typing import Tuple, List, Set, Dict, Any
from dataclasses import dataclass, field

from ..time import Time
from ..identifier import TestId, JobId, DutId
from .run import Run



@dataclass
class Job(Run):
    id              : JobId
    test            : TestId
    dut             : Set[DutId]            = field(default_factory=set)
    args            : List[str]             = field(default_factory=list)
    cwd             : str                   = ""
    env             : Dict[str, str]        = field(default_factory=dict)
    pid             : Optional[int]         = None
    retcode         : Optional[int]         = None

    def __post_init__(self):
        super().__post_init__()
        self.id = JobId(self.id)
        self.test= TestId(self.test)
        self.dut = {DutId(dut) for dut in self.dut}
        self.cwd = str(self.cwd)
        self.env = {str(k): str(v) for k, v in self.env.items()}
        self.args = [str(arg) for arg in self.args]


