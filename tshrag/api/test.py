
# -*- coding: UTF-8 -*-


from typing import Union, Optional, Generic, TypeVar
from typing import Callable, Generator, Iterable, Iterator, AsyncIterator
from typing import Tuple, List, Set, Dict, Any

import json

from pathlib import Path
from dataclasses import dataclass
from dataclasses import asdict
from subprocess import list2cmdline

from fastapi import APIRouter
from fastapi import Query
from pydantic import BaseModel

from ..core import Time
from ..core import Identifier, TestId, JobId, DutId
from ..core import MetricKey, MetricInfo, MetricEntry
from ..core import MetricDB
from ..core import Profile
from ..core import RunStatus, Run, Job, Test
from ..core import Schema

from ..tshrag import Tshrag



_Job = Schema(Job)
_Test = Schema(Test)

class RespTestIdList(BaseModel):
    tests: List[str]

class RespTestDetailList(BaseModel):
    tests: List[_Test]

class RespTestDetail(BaseModel):
    test: _Test

class RespTestJob(BaseModel):
    job: _Job

class RespMessage(BaseModel):
    message: str


def _list_tests(
    tshrag: Tshrag,
    start_time,
    end_time,
    machine,
    device,
):
    _start_time = Time(start_time) if start_time is not None else Time.min
    _end_time = Time(end_time) if end_time is not None else Time.max
    _machine = set(machine)
    _device = set(device)
    _tests = [
        _test
        for _id in tshrag.list_test()
        if (_test := tshrag.query_test(_id))
        if _test.end_time >= _start_time and _test.start_time <= _end_time
        if _machine.issubset(_test.machine)
        if _device.issubset(_test.device)
    ]
    return _tests



def TestAPI(tshrag: Tshrag):
    router = APIRouter()


    @router.get("/tests/id", response_model=RespTestIdList)
    @router.get("/tests", response_model=RespTestIdList)
    def list_tests_id(
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        machine: List[str] = Query([]),
        device: List[str] = Query([]),
    ):
        _tests = [
            str(_test.id)
            for _test in _list_tests(
                tshrag,
                start_time,
                end_time,
                machine,
                device,
            )
        ]
        return RespTestIdList(tests=_tests)


    @router.get("/tests/detail", response_model=RespTestDetailList)
    def list_tests_detail(
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        machine: List[str] = Query([]),
        device: List[str] = Query([]),
    ):
        _tests = [
            _Test.fromcore(_test)
            for _test in _list_tests(
                tshrag,
                start_time,
                end_time,
                machine,
                device,
            )
        ]
        return RespTestDetailList(tests=_tests)


    @router.post("/test", response_model=RespTestDetail)
    def create_test(
        profile: Dict,
        start_time: Optional[str],
        end_time: Optional[str],
        machine: List[str] = Query([]),
        device: List[str] = Query([]),
        env: List[str] = Query([]),
    ):
        _profile = Profile(**profile)
        _start_time = Time(start_time) if start_time is not None else Time.min
        _end_time = Time(end_time) if end_time is not None else Time.max
        _machine = set(machine)
        _device = set(device)
        _env = {
            k: v
            for k, v in
            (i.split("=", 1) for i in env)
        }
        _test = tshrag.create_test(
            profile=_profile,
            start_time=_start_time,
            end_time=_end_time,
            machine=_machine,
            device=_device,
            env=_env,
        )
        _test = _Test.fromcore(_test)
        return RespTestDetail(test=_test)


    @router.get("/test/{test_id}/detail", response_model=RespTestDetail)
    def get_test_detail(
        test_id: str,
    ):
        _test_id = TestId(test_id)
        _test = tshrag.query_test(_test_id)
        _test = _Test.fromcore(_test)
        return RespTestDetail(test=_test)


    @router.get("/test/{test_id}/job/{job_id}", response_model=RespTestJob)
    def get_test_job(
        test_id: str,
        job_id: str,
    ):
        _test_id = TestId(test_id)
        _job_id = JobId(job_id)
        _job = tshrag.query_job(_test_id, _job_id)
        _job = _Job.fromcore(_job)
        return RespTestJob(job=_job)


    @router.post("/test/{test_id}/reschedule", response_model=RespMessage)
    def reschedule_test(
        test_id     : str,
        start_time  : Optional[str]         = Query(None),
        end_time    : Optional[str]         = Query(None),
        duration    : Optional[int]         = Query(None),
    ):
        _test_id = TestId(test_id)
        _start_time = start_time and Time(start_time)
        _end_time = end_time and Time(end_time)
        _duration = duration and int(duration)
        if(tshrag.reschedule_test(_test_id, _start_time, _end_time, _duration)):
            return RespMessage(message=f"Test {test_id} rescheduled.")
        else:
            raise Exception(f"Test {test_id} failed reschedule.")


    @router.post("/test/{test_id}/start", response_model=RespMessage)
    def start_test(
        test_id: str,
    ):
        _test_id = TestId(test_id)
        if(tshrag.startnow_test(_test_id)):
            return RespMessage(message=f"Test {test_id} started.")
        else:
            raise Exception(f"Test {test_id} failed start.")


    @router.post("/test/{test_id}/stop", response_model=RespMessage)
    def stop_test(
        test_id: str,
    ):
        _test_id = TestId(test_id)
        if(tshrag.stopnow_test(_test_id)):
            return RespMessage(message=f"Test {test_id} stopped.")
        else:
            raise Exception(f"Test {test_id} failed stop.")


    @router.post("/test/{test_id}/cancel", response_model=RespMessage)
    def cancel_test(
        test_id: str,
    ):
        _test_id = TestId(test_id)
        if(tshrag.cancel_test(_test_id)):
            return RespMessage(message=f"Test {test_id} cancelled.")
        else:
            raise Exception(f"Test {test_id} failed cancel.")


    return router

