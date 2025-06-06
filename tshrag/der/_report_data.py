# -*- coding: UTF-8 -*-


from typing import Union, Optional, Generic, TypeVar
from typing import Callable, Generator, Iterable, Iterator, AsyncIterator
from typing import Tuple, List, Set, Dict, Any

from ..core import Time
from ..core import Identifier, TestId, JobId, DutId
from ..core import MetricKey, MetricInfo, MetricEntry
from ..core import MetricDB
from ..core import Profile
from ..core import RunStatus, Run, Job, Test
from ..core import StatisticValue, Statistic
from ..core import RuleLevel, Rule, RuleViolation
from ..core import ViewEntry, ViewSection, ViewItem, View
from ..core import ReportEntry, ReportSection, ReportItem, Report

from ..tshrag import Tshrag

from ..util.config import Config

from ..util.consts import SYM_TSHRAG
from ..util.consts import PATH_LOCK
from ..util.consts import TIMEOUT
from ..util.consts import ENCODING
from ..util.consts import CONCURRENCY

from ..util.consts import ENV_PREFIX
from ..util.consts import ENV_HOST
from ..util.consts import ENV_TEST_ID
from ..util.consts import ENV_TEST_MACHINE
from ..util.consts import ENV_TEST_DEVICE
from ..util.consts import ENV_JOB_ID
from ..util.consts import ENV_JOB_MACHINE
from ..util.consts import ENV_JOB_DEVICE
from ..util.consts import ENV_JOB_DIR



def report_data(
    mdb             : MetricDB,
    key             : str,
    statistic       : str,
    start_time      : Optional[Time]        = None,
    end_time        : Optional[Time]        = None,
) -> Dict[str, Any]:
    _statistic = Statistic.from_mdb_query(
        mdb=mdb,
        key=key,
        start_time=start_time,
        end_time=end_time,
    )
    _value = getattr(_statistic, statistic)
    return {statistic: _value}



