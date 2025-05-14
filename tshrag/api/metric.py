
# -*- coding: UTF-8 -*-


from fastapi import APIRouter

from ..core import Time
from ..core import Identifier, TestId, JobId, DutId
from ..core import MetricKey, MetricInfo, MetricEntry
from ..core import MetricDB

from ..tshrag import Tshrag



def MetricAPI(tshrag: Tshrag):
    router = APIRouter()

    return router

