
# -*- coding: UTF-8 -*-


import uuid
import json
import shutil
import time
import os

from pathlib import Path
from contextlib import contextmanager
from dataclasses import asdict
from typing import Union, Optional, Generic, TypeVar
from typing import Generator, Iterable, Iterator, AsyncIterator
from typing import Tuple, List, Set, Dict, Any

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


class Tshrag:


    FILE_LOCK = PATH_LOCK
    FILE_STATUS = "status.json"
    FILE_UPDATE = "update.json"
    FILE_METRIC = "metric.db"


    def __init__(
        self,
        root: Path,
        timeout = TIMEOUT,
        encoding = ENCODING,
        config: Config = None
    ):
        self._root = Path(root)
        self._timeout = timeout
        self._encoding = encoding
        if not config is None:
            config.pick_to(Tshrag.__name__, self)
        self._root.mkdir(parents=True, exist_ok=True)


    def _glob_test(self) -> Generator[TestId, None, None]:
        for _path in self._root.glob(f"*/{Tshrag.FILE_META}"):
            yield TestId(_path.parent.name)

    def _get_test_path(self, test_id: TestId) -> Path:
        return self._root / test_id

    def _get_test_lock(self, test_id: TestId) -> Path:
        return self._get_test_path(test_id) / Tshrag.FILE_LOCK

    def _get_test_status(self, test_id: TestId) -> Path:
        return self._get_test_path(test_id) / Tshrag.FILE_STATUS

    def _get_test_metric(self, test_id: TestId) -> Path:
        return self._get_test_path(test_id) / Tshrag.FILE_METRIC

    def _get_job_path(self, test_id: TestId, job_id: JobId) -> Path:
        return self._get_test_path(test_id) / job_id

    @contextmanager
    def _lock(self, id: TestId):
        with Lock(self._get_test_lock(id), timeout=self._timeout) as lock:
            yield lock

    def _get_test(self, id: TestId) -> Test:
        with self._get_test_status(id).open("r", encoding=self._encoding) as fp:
            return Test(**json.load(fp))

    def _set_test(self, test: Test):
        with self._get_test_status(test.id).open("w", encoding=self._encoding) as fp:
            json.dump(asdict(test), fp, default=lambda value : str(value))


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
        _id = TestId(profile.name + str(uuid.uuid4()))
        _start_time = Time(start_time)
        _end_time = Time(end_time)
        _machine = machine or set()
        _device = device or set()
        _env = env or dict()
        _mdb = MetricDB(self._get_test_metric(_id))
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
        self._get_test_path(_id).mkdir(parents=True, exist_ok=True)
        with self._lock(id) as lock:
            self._set_test(_test)
        return _test


    def query_test(self, id: TestId) -> Optional[Test]:
        try:
            return self._get_test(id)
        except:
            return None


    @contextmanager
    def update_test(self, id: TestId) -> Generator[Test, None, None]:
        with self._lock(id) as lock:
            test = self._get_test(id)
            try:
                yield test
            finally:
                self._set_test(test)


