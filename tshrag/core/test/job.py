
# -*- coding: UTF-8 -*-


from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .load import Load
from .run import Run



@dataclass
class Job(Run):
    id              : str
    test_id         : str
    load            : Load
    env             : Dict[str, str]        = field(default_factory=dict)
    args            : List[str]             = field(default_factory=list)
    pid             : Optional[int]         = None
    retcode         : Optional[int]         = None

    def __post_init__(self):
        super().__post_init__()
        self.id = self.id.lower()
