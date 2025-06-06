# -*- coding: UTF-8 -*-


from types import NoneType
from typing import Optional, Union
from typing import Iterable, Tuple, List, Set, Dict, Any
from typing import get_type_hints, get_origin, get_args

from dataclasses import dataclass, field
from contextlib import suppress

from ..time import Time
from ..identifier import TestId, JobId, DutId
from ..metric import MetricDB



StatisticValue = Optional[Union[float, int]]

def _StatisticValue(v: str) -> StatisticValue:
    with suppress(TypeError, ValueError):
        return int(v)
    with suppress(TypeError, ValueError):
        return float(v)
    return None


@dataclass
class Statistic:
    raw             : List[Tuple[Time, str]] = field(default_factory=list)
    hist            : Dict[str, int]        = field(default_factory=dict)
    vtimes          : List[Time]            = field(default_factory=list)
    values          : List[StatisticValue]  = field(default_factory=list)
    cnt             : Optional[int]         = None
    cntval          : Optional[int]         = None
    cntnan          : Optional[int]         = None
    sum             : StatisticValue        = None
    avg             : StatisticValue        = None
    min             : StatisticValue        = None
    max             : StatisticValue        = None

    def __post_init__(self):
        self.hist = {}
        for v in self.raw:
            _v = str(v)
            if _v not in self.hist:
                self.hist[_v] = 0
            self.hist[_v] += 1
        time_values = [
            (t, _v)
            for t, v in self.raw
            if (_v := _StatisticValue(v)) is not None
        ]
        self.vtimes = [t for t, _ in time_values]
        self.values = [v for _, v in time_values]
        self.cnt = len(self.raw)
        self.cntval = sum(1 for v in self.values if v is not None)
        self.cntnan = sum(1 for v in self.values if v is None)
        if not self.values:
            self.sum = None
            self.avg = None
            self.min = None
            self.max = None
        else:
            self.sum = sum(v for v in self.values)
            self.avg = self.sum / self.cntval
            self.min = min(self.values)
            self.max = max(self.values)

    @classmethod
    def from_mdb_query(
        cls,
        mdb             : MetricDB,
        key             : str,
        test            : TestId            = None,
        dut             : Union[DutId, Set[DutId]] = None,
        start_time      : Time              = None,
        end_time        : Time              = None,
    ) -> 'Statistic':
        _entries = mdb.query_metric_entry(
            key=key,
            test=test,
            dut=dut,
            start_time=start_time,
            end_time=end_time,
        )
        _raw = [
            (_e.time, _e.value)
            for _e in _entries
        ]
        return cls(raw=_raw)


