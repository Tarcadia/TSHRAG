# -*- coding: UTF-8 -*-


from typing import Union, Optional, Generic, TypeVar
from typing import Callable, Generator, Iterable, Iterator, AsyncIterator
from typing import Tuple, List, Set, Dict, Any

import re
import shlex

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
from ._report_data import report_data

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


_OPERATORS = {
    "==" : lambda x, y: float(x) == float(y),
    "!=" : lambda x, y: float(x) != float(y),
    "<"  : lambda x, y: float(x) < float(y),
    "<=" : lambda x, y: float(x) <= float(y),
    ">"  : lambda x, y: float(x) > float(y),
    ">=" : lambda x, y: float(x) >= float(y),
    "=~" : lambda x, y: re.match(str(y), str(x)) is not None,
    "~"  : lambda x, y: re.search(str(y), str(x)) is not None,
    "!~" : lambda x, y: re.search(str(y), str(x)) is None,
}

_OPERATOR_PATT_SUB = "|".join(
    re.escape(_op)
    for _op in [*_OPERATORS, ":"]
)

_CONDITION_PATT = re.compile(
    r"^\s*"
    r"(?P<statistic>[a-zA-Z_][a-zA-Z0-9_]*)"
    r"\s*"
    r"(?P<operator>" + _OPERATOR_PATT_SUB + r")"
    r"\s*"
    r"(?P<value>.+?)"
    r"\s*$",
    re.IGNORECASE
)



def _judge_operator(
    statistic       : str,
    operator        : str,
    value           : str,
    mdb             : MetricDB,
    key             : str,
    rule            : Rule,
    start_time      : Optional[Time]        = None,
    end_time        : Optional[Time]        = None,
) -> List[RuleViolation]:
    _violations = []
    if not statistic:
        _entries = mdb.query_metric_entry(
            key=key,
            start_time=start_time,
            end_time=end_time,
        )
        _entries = [
            _entry
            for _entry in _entries
            if _OPERATORS[operator](
                _entry.value,
                value,
            )
        ]
        if _entries:
            _violations.append(
                RuleViolation(
                    description=rule.description,
                    condition=rule.condition,
                    level=rule.level,
                    key=key,
                    statistic=statistic,
                    when=[_entry.time for _entry in _entries],
                )
            )
    else:
        _statistic = Statistic.from_mdb_query(
            mdb=mdb,
            key=key,
            start_time=start_time,
            end_time=end_time,
        )
        _value = getattr(_statistic, statistic)
        try:
            if not _OPERATORS[operator](_value, value):
                _violations.append(
                    RuleViolation(
                        description=rule.description,
                        condition=rule.condition,
                        level=rule.level,
                        key=key,
                        statistic=statistic,
                        when=[start_time, end_time],
                    )
                )
        except (TypeError, ValueError) as e:
            # TODO: Handle error
            pass
    return _violations


def _judge_special(
    special         : str,
    args            : List[str],
    mdb             : MetricDB,
    key             : str,
    rule            : Rule,
    start_time      : Optional[Time]        = None,
    end_time        : Optional[Time]        = None,
) -> List[RuleViolation]:
    return []


def report_judge(
    mdb             : MetricDB,
    key             : str,
    rule            : Rule,
    start_time      : Optional[Time]        = None,
    end_time        : Optional[Time]        = None,
) -> List[RuleViolation]:
    _violations = []
    _match = _CONDITION_PATT.match(rule.condition)
    if not _match:
        raise ValueError(f"Invalid rule condition: {rule.condition}")
    _statistic = _match.group("statistic")
    _operator = _match.group("operator")
    _value = _match.group("value").strip()
    if _operator in _OPERATORS:
        _violations = _judge_operator(
            statistic=_statistic,
            operator=_operator,
            value=_value,
            mdb=mdb,
            key=key,
            rule=rule,
            start_time=start_time,
            end_time=end_time,
        )
    elif _operator == ":" and _statistic:
        _violations = _judge_special(
            special=_statistic,
            args=shlex.split(_value),
            mdb=mdb,
            key=key,
            rule=rule,
            start_time=start_time,
            end_time=end_time,
        )
    elif _operator == ":" and not _statistic:
        raise ValueError(f"Invalid rule condition: {rule.condition}")
    else:
        raise ValueError(f"Unknown operator: {rule.condition}")
    return _violations


