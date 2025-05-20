
# -*- coding: UTF-8 -*-


from enum import Enum
from dataclasses import dataclass

from ..time import Time



class RunStatus(str, Enum):
    PENDING         = "PENDING"
    PREPARING       = "PREPARING"
    RUNNING         = "RUNNING"
    COMPLETED       = "COMPLETED"
    CRASHED         = "CRASHED"
    CANCELLED       = "CANCELLED"



@dataclass
class Run:
    status          : RunStatus
    start_time      : Time
    end_time        : Time

    def __post_init__(self):
        if isinstance(self.status, str):
            self.status = RunStatus(self.status.upper())
        if isinstance(self.start_time, str):
            self.start_time = Time(self.start_time)
        if isinstance(self.end_time, str):
            self.end_time = Time(self.end_time)


