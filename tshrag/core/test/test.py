
# -*- coding: UTF-8 -*-


from typing import Union, Optional, Generic, TypeVar
from typing import Iterable, Iterator, AsyncIterator
from typing import Tuple, List, Set, Dict, Any
from dataclasses import dataclass, field

from ..time import Time
from ..identifier import TestId, JobId, DutId
from ..profile import Profile

from .run import Run



@dataclass
class Test(Run):
    test            : TestId
    dut             : Set[DutId]            = field(default_factory=set)
    env             : Dict[str, str]        = field(default_factory=dict)
    profile         : Optional[Profile]     = None

    def __post_init__(self):
        super().__post_init__()
        self.test = TestId(self.test)
        self.dut = {DutId(dut) for dut in self.dut}
        self.env = {str(k): str(v) for k, v in self.env.items()}
        if isinstance(self.profile, dict):
            self.profile = Profile(**self.profile)

