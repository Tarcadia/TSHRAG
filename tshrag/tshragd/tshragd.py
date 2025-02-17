
# -*- coding: UTF-8 -*-


import uuid
import json
import shutil
import time

from pathlib import Path
from contextlib import contextmanager
from dataclasses import asdict
from typing import List, Generator, Optional

from portalocker import Lock

from ..core import Time
from ..core import MetricId, MetricIdPattern, Metric, MetricEntry, Mdb
from ..core import RunStatus
from ..core import JobId, Job
from ..core import TestId, Test
from ..core import Profile

from ..util.config import Config

from ..util.consts import SYM_TSHRAG
from ..util.consts import PATH_LOCK
from ..util.consts import TIMEOUT
from ..util.consts import ENCODING

from .distributor import distribute
from .executor import execute
from .reporter import report



class Tshragd:

    TSHRAGD_FILE_LOCK = PATH_LOCK

    TSHRAGD_PATH_MDB = "mdb"
    TSHRAGD_PATH_TESTS = "tests"
    TSHRAGD_PATH_LOADS = "loads"
    TSHRAGD_FILE_INDEX = "index.json"

    TSHRAGD_CONFIG_SESSIONS = [SYM_TSHRAG, "tshragd"]

    def __init__(
        self, root: Path,
        timeout = TIMEOUT,
        encoding = ENCODING,
        config: Config = None
    ):
        self._root = Path(root)
        self._timeout = timeout
        self._encoding = encoding
        if not config is None:
            for _session in Tshragd.TSHRAGD_CONFIG_SESSIONS:
                config.pick_to(_session, self)
        
        self._root.mkdir(parents=True, exist_ok=True)


    @contextmanager
    def _lock(self):
        with Lock(self._get_lock_file(), timeout=self._timeout) as _l:
            yield _l


    def _get_lock_file(self) -> Path:
        return self._root / Tshragd.TSHRAGD_FILE_LOCK


    def _get_index_file(self) -> Path:
        return self._root / Tshragd.TSHRAGD_FILE_INDEX


    def _get_tests_path(self) -> Path:
        return self._root / Tshragd.TSHRAGD_PATH_TESTS


    def _get_test_path(self, test_id: TestId) -> Path:
        return self._get_tests_path() / test_id


    def _get_test_file(self, test_id: TestId) -> Path:
        return self._get_test_path(test_id) / Tshragd.TSHRAGD_FILE_INDEX


    def _glob_test_file(self) -> Generator[Path, None, None]:
        for _index in self._get_tests_path().glob(f"*/{Tshragd.TSHRAGD_FILE_INDEX}"):
            yield _index


    def _get_job_path(self, test_id: TestId, job_id: JobId) -> Path:
        return self._get_test_path(test_id) / job_id


    def _get_test_mdb_path(self, test_id: TestId) -> Path:
        return self._get_test_path(test_id) / Tshragd.TSHRAGD_PATH_MDB


    def _get_job_mdb_path(self, test_id: TestId, job_id: JobId) -> Path:
        return self._get_job_path(test_id, job_id) / Tshragd.TSHRAGD_PATH_MDB


    def _get_test(self, id: TestId) -> Test:
        with self._get_test_file(id).open("r", encoding=self._encoding) as fp:
            return Test(**json.load(fp))


    def _set_test(self, test: Test):
        with self._get_test_file(id).open("w", encoding=self._encoding) as fp:
            json.dump(asdict(test), fp, default=lambda value : str(value))


    def _get_job(self, test_id: TestId, job_id: JobId) -> Job:
        _test = self._get_test(test_id)
        for job in _test.jobs:
            if job.id == job_id:
                return job
        return None


    def _get_test_mdb(self, test_id: TestId) -> Mdb:
        return Mdb(self._get_test_mdb_path(test_id))


    def _get_job_mdb(self, test_id: TestId, job_id: JobId) -> Mdb:
        return Mdb(self._get_job_mdb_path(test_id, job_id))


    def _list_mdb(self, test_id: TestId) -> List[Mdb]:
        _mdbs = []
        _test = self._get_test(test_id)
        try:
            _mdbs.append(self._get_test_mdb(_test.id))
        except:
            # TODO: Log error
            pass
        for _job in _test.jobs:
            try:
                _mdb = self._get_job_mdb(_test.id, _job.id)
            except:
                # TODO: Log error
                continue
            _mdbs.append(_mdb)
        return _mdbs


    def _list_metric(self, test_id: TestId, metric_id_pattern: MetricIdPattern) -> List[Metric]:
        _metrics = []
        _mdbs = self._list_mdb(test_id)
        for _mdb in _mdbs:
            try:
                _metrics = _mdb.list(metric_id_pattern)
            except:
                # TODO: Log error
                continue
            _metrics.extend(_metrics)
        return _metrics


    def _range_test(self, start_time: Time, end_time: Time) -> List[Test]:
        _tests = []
        for _index in self._glob_test_file():
            try:
                with _index.open("r") as fp:
                    _test = Test(**json.load(fp))
            except:
                # TODO: Log error
                continue
            if _test.id == _index.parent.name:
                if start_time <= _test.end_time and _test.start_time <= end_time:
                    _tests.append(_test)
            _tests.sort(key=lambda test : test.start_time)
        return _tests


    def _get_metric(self, test_id: TestId, metric_id: MetricId) -> Metric:
        _metric = None
        _mdbs = self._list_mdb(test_id)
        for _mdb in _mdbs:
            try:
                _m = _mdb.get(metric_id)
            except:
                continue
            if _m and not _metric:
                _metric = _m
            elif _m and _metric and _m != _metric:
                # TODO: Log conflict metric error
                pass
        return _metric


    def _read_metric(self, test_id: TestId, metric_id: MetricId, start_time: Time, end_time: Time) -> List[MetricEntry]:
        _metric = None
        _entries = []
        _mdbs = self._list_mdb(test_id)
        for _mdb in _mdbs:
            try:
                _m = _mdb.get(metric_id)
                _e = _mdb.read(metric_id, start_time, end_time)
            except:
                continue
            if _m and not _metric:
                _metric = _m
                _entries.extend(_e)
            elif _m and _metric and _m == _metric:
                _entries.extend(_e)
            elif _m and _metric and _m != _metric:
                # TODO: Log conflict metric error
                pass
        return _entries


    def create_test(self, profile: Profile, start_time: Time, end_time: Time) -> Optional[TestId]:

        start_time = Time(start_time)
        end_time = Time(end_time)
        test = Test(
            status=RunStatus.PENDING,
            start_time=start_time,
            end_time=end_time,
            id=TestId(profile.name + str(start_time)),
            profile=profile,
            dut={}, jobs=[]
        )

        test_id = None
        try:
            with self._lock():
                _tests = self._range_test(start_time, end_time)
                _test = self._get_test_file(test.id)
                if _tests:
                    raise ValueError(f"Test timeslot occupied: {[_t.id for _t in _tests]}")
                if _test.exists():
                    raise ValueError(f"Test exists: {test.id}")
                self._set_test(test)
                test_id = test.id
        except:
            # TODO: Log error
            pass
        return test_id


    def list_test(self, start_time: Time, end_time: Time) -> List[Test]:
        start_time = Time(start_time)
        end_time = Time(end_time)
        tests = []
        try:
            tests = self._range_test(start_time, end_time)
        except:
            # TODO: Log error
            pass
        return tests


    def get_test(self, test_id: TestId) -> Test:
        test_id = TestId(test_id)
        test = None
        try:
            test = self._get_test(test_id)
        except:
            # TODO: Log error
            pass
        return test


    def get_job(self, test_id: TestId, job_id: JobId) -> Job:
        test_id = TestId(test_id)
        job_id = JobId(job_id)
        job = None
        try:
            job = self._get_job(test_id, job_id)
        except:
            # TODO: Log error
            pass
        return job


    def list_metric(self, test_id: TestId, metric_id_pattern: MetricIdPattern = MetricIdPattern()) -> List[Metric]:
        test_id = TestId(test_id)
        metric_id_pattern = MetricIdPattern(metric_id_pattern)
        metrics = []
        try:
            metrics = self._list_metric(test_id, metric_id_pattern)
        except:
            # TODO: Log error
            pass
        return metrics


    def get_metric(self, test_id: TestId, metric_id: MetricId) -> Metric:
        test_id = TestId(test_id)
        metric_id = MetricId(metric_id)
        metric = None
        try:
            metric = self._get_metric(test_id, metric_id)
        except:
            # TODO: Log error
            pass
        return metric


    def read_metric(self, test_id: TestId, metric_id: MetricId, start_time: Time, end_time: Time) -> List[MetricEntry]:
        test_id = TestId(test_id)
        metric_id = MetricId(metric_id)
        entries = []
        try:
            entries = self._read_metric(test_id, metric_id, start_time, end_time)
        except:
            # TODO: Log error
            pass
        return entries


    def main(self):
        while True:
            with self._lock():
                _tests_expire = [_test.status == RunStatus.PENDING for _test in self._range_test(Time.min, Time())]
                _tests_todo = [_test.status == RunStatus.PENDING for _test in self._range_test(Time(), Time.max)]
                for _test in _tests_expire:
                    if _test.status == RunStatus.PENDING:
                        _test.status = RunStatus.CANCELLED
                        self._set_test(_test)
                if not _tests_todo:
                    time.sleep(self._timeout)
                    continue
                elif _tests_todo[0].start_time > Time():
                    _sleep = (_tests_todo[0].start_time - Time()).seconds
                    _sleep = min(self._timeout, _sleep)
                    time.sleep(_sleep)
                    continue
                else:
                    # TODO: Launch Test
                    _test = _tests_todo[0]
                    _loads = {}
                    for _load in _test.profile.bom:
                        _loads[_load] = distribute(_test.profile.bom[_load])
                    execute(_test, _loads, self._get_test_path(_test.id))


