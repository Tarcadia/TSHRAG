
# -*- coding: UTF-8 -*-


from fastapi import APIRouter

from ..core import Time
from ..core import Identifier, TestId, JobId, DutId
from ..core import MetricKey, MetricInfo, MetricEntry
from ..core import MetricDB
from ..core import Profile
from ..core import RunStatus, Run, Job, Test

from ..tshrag import Tshrag



def TestAPI(tshrag: Tshrag):
    router = APIRouter()

    @router.get("/tests")
    def get_tests():
        return tshrag.list_test()

    @router.get("/test/{test_id}")
    def get_test(test_id: TestId):
        return tshrag.query_test(test_id)

    return router

