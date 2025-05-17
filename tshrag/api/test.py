
# -*- coding: UTF-8 -*-


from typing import Union, Optional, Generic, TypeVar
from typing import Callable, Generator, Iterable, Iterator, AsyncIterator
from typing import Tuple, List, Set, Dict, Any

import json

from pathlib import Path
from dataclasses import asdict
from subprocess import list2cmdline

from fastapi import APIRouter
from fastapi import Query

from ..core import Time
from ..core import Identifier, TestId, JobId, DutId
from ..core import MetricKey, MetricInfo, MetricEntry
from ..core import MetricDB
from ..core import Profile
from ..core import RunStatus, Run, Job, Test

from ..tshrag import Tshrag



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


    @router.get("/tests/id")
    @router.get("/tests")
    def list_tests_id(
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        machine: List[str] = Query([]),
        device: List[str] = Query([]),
    ):
        _tests = [
            _test.id
            for _test in _list_tests(
                tshrag,
                start_time,
                end_time,
                machine,
                device,
            )
        ]
        return _tests


    @router.get("/tests/detail")
    def list_tests_detail(
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        machine: List[str] = Query([]),
        device: List[str] = Query([]),
    ):
        _tests = [
            asdict(_test)
            for _test in _list_tests(
                tshrag,
                start_time,
                end_time,
                machine,
                device,
            )
        ]
        return _tests


    @router.post("/test")
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
        return asdict(_test)


    @router.get("/test/{test_id}/detail")
    def get_test_detail(
        test_id: str,
    ):
        _test_id = TestId(test_id)
        _test = tshrag.query_test(_test_id)
        return asdict(_test)


    @router.get("/test/{test_id}/job/{job_id}")
    def get_test_job(
        test_id: str,
        job_id: str,
    ):
        _test_id = TestId(test_id)
        _job_id = JobId(job_id)
        _job = tshrag.query_job(_test_id, _job_id)
        return asdict(_job)


    @router.post("/test/{test_id}/reschedule")
    def reschedule_test(
        test_id: str,
        start_time: Optional[str],
        end_time: Optional[str],
    ):
        _test_id = TestId(test_id)
        _start_time = start_time and Time(start_time)
        _end_time = end_time and Time(end_time)
        if(tshrag.reschedule_test(_test_id, _start_time, _end_time)):
            return f"Test {test_id} rescheduled."
        else:
            raise Exception(f"Test {test_id} failed reschedule.")


    @router.post("/test/{test_id}/start")
    def start_test(
        test_id: str,
    ):
        _test_id = TestId(test_id)
        if(tshrag.startnow_test(_test_id)):
            return f"Test {test_id} started."
        else:
            raise Exception(f"Test {test_id} failed start.")


    @router.post("/test/{test_id}/stop")
    def stop_test(
        test_id: str,
    ):
        _test_id = TestId(test_id)
        if(tshrag.stopnow_test(_test_id)):
            return f"Test {test_id} stopped."
        else:
            raise Exception(f"Test {test_id} failed stop.")


    @router.post("/test/{test_id}/cancel")
    def cancel_test(
        test_id: str,
    ):
        _test_id = TestId(test_id)
        if(tshrag.cancel_test(_test_id)):
            return f"Test {test_id} cancelled."
        else:
            raise Exception(f"Test {test_id} failed cancel.")


    return router

