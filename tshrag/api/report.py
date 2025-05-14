
# -*- coding: UTF-8 -*-


from fastapi import APIRouter

from ..core import Time
from ..core import Identifier, TestId, JobId, DutId
from ..core import MetricKey, MetricInfo, MetricEntry
from ..core import MetricDB
from ..core import Profile
from ..core import RunStatus, Run, Job, Test

from ..tshrag import Tshrag



def ReportAPI(tshrag: Tshrag):
    router = APIRouter()

    return router

