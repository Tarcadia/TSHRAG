# -*- coding: UTF-8 -*-


from typing import Union, Optional, Generic, TypeVar
from typing import Callable, Generator, Iterable, Iterator, AsyncIterator
from typing import Tuple, List, Set, Dict, Any

import uuid
import json
import shutil
import time
import os
import shlex

from pathlib import Path
from threading import Thread
from subprocess import Popen

import seqript.seqript
import seqript.engine
import seqript.engine.contrib
from seqript.seqript import Seqript
from seqript.util import expand_variable, expand_variable_dict

from ..core import Time
from ..core import Identifier, TestId, JobId, DutId
from ..core import MetricKey, MetricInfo, MetricEntry
from ..core import MetricDB
from ..core import Profile
from ..core import RunStatus, Run, Job, Test
from ..core import RuleLevel, Rule
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



def _reporting(
    view            : dict,
    rules           : List[dict],
    **kwargs,
) -> Tuple[View, List[Rule]]:
    _view = View(**view)
    _rules = [Rule(**_rule) for _rule in rules]
    return _view, _rules


def _judge_rule(
    mdb             : MetricDB,
    rule            : Rule,
    start_time      : Optional[Time]        = None,
    end_time        : Optional[Time]        = None,
) -> bool:
    pass

def _render_entry(
    mdb             : MetricDB,
    entry           : ViewEntry,
    start_time      : Optional[Time]        = None,
    end_time        : Optional[Time]        = None,
) -> ReportEntry:
    return ReportEntry(
        key=entry.key,
        name=entry.name,
        description=entry.description,
        style=entry.style,
        violations=[],
        data={},
    )

def _render_section(
    mdb             : MetricDB,
    section         : ViewSection,
    start_time      : Optional[Time]        = None,
    end_time        : Optional[Time]        = None,
) -> ReportSection:
    return ReportSection(
        name=section.name,
        items=[
            _render_item(
                mdb=mdb,
                item=item,
                start_time=start_time,
                end_time=end_time,
            )
            for item in section.items
        ]
    )

def _render_item(
    mdb             : MetricDB,
    item            : ViewItem,
    start_time      : Optional[Time]        = None,
    end_time        : Optional[Time]        = None,
) -> ReportItem:
    if isinstance(item, ViewEntry):
        return _render_entry(
            mdb=mdb,
            entry=item,
            start_time=start_time,
            end_time=end_time,
        )
    elif isinstance(item, ViewSection):
        return _render_section(
            mdb=mdb,
            section=item,
            start_time=start_time,
            end_time=end_time,
        )
    else:
        raise TypeError(f"Unknown item type: {type(item)}")

def _render(
    mdb             : MetricDB,
    view            : View,
    start_time      : Optional[Time]        = None,
    end_time        : Optional[Time]        = None,
) -> List[ReportSection]:
    return [
        _render_section(
            mdb=mdb,
            section=_section,
            start_time=start_time,
            end_time=end_time,
        )
        for _section in view.sections
    ]


def report(
    tshrag          : Tshrag,
    test_id         : TestId,
    start_time      : Optional[Time]        = None,
    end_time        : Optional[Time]        = None,
) -> Report:
    _test = tshrag.query_test(test_id)
    _mdb = _test.get_mdb()
    _view, _rules = _reporting(**_test.profile.reporting)
    _jobs = [
        _job
        for _job_id in _test.jobs
        if (_job := tshrag.query_job(_test.id, _job_id))
        if (end_time is None) or (_job.start_time < end_time)
        if (start_time is None) or (_job.end_time > start_time)
    ]
    _sections = _render(
        mdb=_mdb,
        view=_view,
        start_time=start_time,
        end_time=end_time,
    )
    _report = Report(
        id=_test.id,
        profile=_test.profile,
        start_time=_test.start_time,
        end_time=_test.end_time,
        machine=_test.machine,
        device=_test.device,
        env=_test.env,
        jobs=_jobs,
        sections=_sections
    )
    return _report


