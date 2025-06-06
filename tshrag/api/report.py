# -*- coding: UTF-8 -*-


from typing import Union, Optional, Generic, TypeVar
from typing import Callable, Generator, Iterable, Iterator, AsyncIterator
from typing import Tuple, List, Set, Dict, Any

from fastapi import APIRouter
from fastapi import Query
from pydantic import BaseModel

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
from ..core import Schema

from ..tshrag import Tshrag



_Report = Schema(Report)

class RespReport(BaseModel):
    report          : _Report

class RespMessage(BaseModel):
    message         : str


def ReportAPI(tshrag: Tshrag):
    router = APIRouter()


    @router.get("/test/{test_id}/report", response_model=RespReport)
    def get_test_report(
        test_id     : str,
        start_time  : Optional[str]         = Query(None),
        end_time    : Optional[str]         = Query(None),
    ) -> RespReport:
        """Get the report for a specific test."""
        _test_id = TestId(test_id)
        _start_time = start_time and Time(start_time)
        _end_time = end_time and Time(end_time)
        _report = tshrag.report_test(
            id=_test_id,
            start_time=_start_time,
            end_time=_end_time,
        )
        _report = _Report.fromcore(_report)
        return RespReport(report=_report)


    return router

