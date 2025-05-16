
# -*- coding: UTF-8 -*-


from typing import Union, Optional, Generic, TypeVar
from typing import Callable, Generator, Iterable, Iterator, AsyncIterator
from typing import Tuple, List, Set, Dict, Any

import uuid
import json
import shutil
import time
import os

from pathlib import Path
from contextlib import contextmanager
from dataclasses import asdict
from threading import Thread

from portalocker import Lock

from ..core import Time
from ..core import Identifier, TestId, JobId, DutId
from ..core import MetricKey, MetricInfo, MetricEntry
from ..core import MetricDB
from ..core import Profile
from ..core import RunStatus, Run, Job, Test

from ..util.config import Config

from ..util.consts import SYM_TSHRAG
from ..util.consts import PATH_LOCK
from ..util.consts import TIMEOUT
from ..util.consts import ENCODING
from ..util.consts import CONCURRENCY


class Tshrag:


    FILE_LOCK = PATH_LOCK
    FILE_TEST = "status.json"
    FILE_METRIC = "metric.db"
    PATH_JOBS = "jobs"


    def __init__(
        self,
        root        : Path,
        timeout     : int                   = TIMEOUT,
        encoding    : str                   = ENCODING,
        max_workers : int                   = CONCURRENCY,
        test_main   : Callable[["Tshrag", TestId], None] = None,
        config      : Config                = None
    ):
        self._root = Path(root)
        self._timeout = timeout
        self._encoding = encoding
        self._max_workers = max_workers
        self._test_main = test_main

        if not config is None:
            config.pick_to(Tshrag.__name__, self)
        self._root.mkdir(parents=True, exist_ok=True)
        self._workers = []


    def _get_lock(self) -> Path:
        return self._root / Tshrag.FILE_LOCK

    def _glob_test(self) -> Generator[TestId, None, None]:
        for _path in self._root.glob(f"*/{Tshrag.FILE_TEST}"):
            yield TestId(_path.parent.name)

    def _get_test_path(self, test_id: TestId) -> Path:
        return self._root / test_id

    def _get_test_lock(self, test_id: TestId) -> Path:
        return self._get_test_path(test_id) / Tshrag.FILE_LOCK

    def _get_test_file(self, test_id: TestId) -> Path:
        return self._get_test_path(test_id) / Tshrag.FILE_TEST

    def _get_test_metric(self, test_id: TestId) -> Path:
        return self._get_test_path(test_id) / Tshrag.FILE_METRIC

    def _get_test_job_root(self, test_id: TestId) -> Path:
        return self._get_test_path(test_id) / Tshrag.PATH_JOBS

    def _glob_job(self, test_id: TestId) -> Generator[JobId, None, None]:
        for _path in self._get_test_job_root(test_id).glob("*.json"):
            yield JobId(_path.stem)

    def _get_job_lock(self, test_id: TestId, job_id: JobId) -> Path:
        return self._get_test_job_root(test_id) / f"{job_id}.lock"

    def _get_job_file(self, test_id: TestId, job_id: JobId) -> Path:
        return self._get_test_job_root(test_id) / f"{job_id}.json"

    @contextmanager
    def _lock(self):
        with Lock(self._get_lock(), timeout=self._timeout) as lock:
            yield lock

    @contextmanager
    def _test_lock(self, id: TestId):
        with Lock(self._get_test_lock(id), timeout=self._timeout) as lock:
            yield lock

    @contextmanager
    def _job_lock(self, test_id: TestId, job_id: JobId):
        with Lock(self._get_job_lock(test_id, job_id), timeout=self._timeout) as lock:
            yield lock

    def _get_test(self, id: TestId) -> Test:
        with self._get_test_file(id).open("r", encoding=self._encoding) as fp:
            return Test(**json.load(fp))

    def _set_test(self, test: Test):
        with self._get_test_file(test.id).open("w", encoding=self._encoding) as fp:
            json.dump(asdict(test), fp, default=lambda value : str(value))

    def _get_job(self, test_id: TestId, job_id: JobId) -> Job:
        with self._get_job_file(test_id, job_id).open("r", encoding=self._encoding) as fp:
            return Job(**json.load(fp))

    def _set_job(self, test_id: TestId, job: Job):
        with self._get_job_file(test_id, job.id).open("w", encoding=self._encoding) as fp:
            json.dump(asdict(job), fp, default=lambda value : str(value))


    def list_test(self) -> List[TestId]:
        return list(self._glob_test())


    def create_test(
        self,
        profile     : Profile,
        start_time  : Time                  = None,
        end_time    : Time                  = Time.max,
        machine     : Set[str]              = None,
        device      : Set[str]              = None,
        env         : Dict[str, str]        = None,
    ) -> Test:
        _id = TestId(f"{profile.name}-{uuid.uuid4()}")
        self._get_test_path(_id).mkdir(parents=True, exist_ok=True)
        _start_time = Time(start_time)
        _end_time = Time(end_time)
        _machine = machine or set()
        _device = device or set()
        _env = env or dict()
        _mdb = self._get_test_metric(_id)
        _test = Test(
            id = _id,
            profile = profile,
            status = RunStatus.PENDING,
            start_time = _start_time,
            end_time = _end_time,
            machine = _machine,
            device = _device,
            env = _env,
            mdb = _mdb,
        )
        with self._test_lock(_id) as lock:
            self._set_test(_test)
        return _test


    def query_test(self, id: TestId) -> Optional[Test]:
        try:
            return self._get_test(id)
        except:
            return None


    def query_job(self, test_id: TestId, job_id: JobId) -> Optional[Job]:
        try:
            return self._get_job(test_id, job_id)
        except:
            return None


    @contextmanager
    def update_test(self, id: TestId) -> Generator[Test, None, None]:
        with self._test_lock(id) as lock:
            test = self._get_test(id)
            try:
                yield test
            finally:
                self._set_test(test)


    @contextmanager
    def update_job(self, test_id: TestId, job_id: JobId) -> Generator[Job, None, None]:
        with self._job_lock(test_id, job_id) as lock:
            job = self._get_job(test_id, job_id)
            try:
                yield job
            finally:
                self._set_job(test_id, job)


    def task(self, id: TestId) -> Thread:
        self._workers = [
            _worker
            for _worker in self._workers
            if _worker.is_alive()
        ]
        if self._test_main is None:
            return None
        if len(self._workers) >= self._max_workers:
            return None
        
        def _wrap():
            with self.update_test(id) as test:
                test.start_time = Time.now()
            try:
                _ret = self._test_main(self, id)
                _status = RunStatus.COMPLETED
            except KeyboardInterrupt:
                _ret = None
                _status = RunStatus.CANCELLED
            except Exception as e:
                # TODO: Handle exception
                _ret = None
                _status = RunStatus.FAILED
            with self.update_test(id) as test:
                test.end_time = Time.now()
                if test.status in (RunStatus.CANCELLED, RunStatus.COMPLETED, RunStatus.FAILED):
                    pass
                elif test.status == RunStatus.RUNNING:
                    test.status = _status
                else:
                    test.status = RunStatus.FAILED
            return _ret
        
        _worker = Thread(
            target = _wrap,
            name = f"{SYM_TSHRAG}_{id}",
        )
        
        try:
            with self.update_test(id) as test:
                if test.status == RunStatus.PENDING:
                    test.status = RunStatus.PREPARING
            _worker.start()
            self._workers.append(_worker)
            return _worker
        except Exception as e:
            # TODO: Logging error
            with self.update_test(id) as test:
                test.status = RunStatus.CANCELLED
                test.end_time = Time.now()
            return None


    def refresh(self) -> None:
        with self._lock() as lock:
            _tests = sorted(
                [
                    self.query_test(id)
                    for id in self.list_test()
                ],
                key = lambda x: x.start_time,
            )
            _occupied = {
                machine
                for test in _tests
                for machine in test.machine
                if test.status == RunStatus.RUNNING
                or test.status == RunStatus.PREPARING
            }
            _tests = [
                test
                for test in _tests
                if test.status == RunStatus.PENDING
                and test.start_time < Time.now()
                and test.end_time > Time.now()
            ]
            for _test in _tests:
                if _occupied.isdisjoint(_test.machine):
                    if self.task(_test.id):
                        _occupied.update(_test.machine)



    def startnow_test(self, id: TestId) -> None:
        with self.update_test(id) as test:
            if test.status == RunStatus.PENDING:
                test.start_time = Time.now()
                return True
        return False


    def endnow_test(self, id: TestId) -> None:
        with self.update_test(id) as test:
            if test.status not in (RunStatus.CANCELLED, RunStatus.COMPLETED, RunStatus.FAILED):
                test.end_time = Time.now()
                return True
        return False


    def cancel_test(self, id: TestId) -> None:
        with self.update_test(id) as test:
            test.status = RunStatus.CANCELLED
            return True
        return False


