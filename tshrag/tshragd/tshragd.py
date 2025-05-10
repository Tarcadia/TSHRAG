
# -*- coding: UTF-8 -*-


import uuid
import json
import shutil
import time

from pathlib import Path
from threading import Thread
from concurrent.futures import ThreadPoolExecutor

from portalocker import Lock

from fastapi import APIRouter

from ..core import Time
from ..core import Identifier, TestId, JobId, DutId
from ..core import MetricKey, MetricInfo, MetricEntry
from ..core import MetricDB
from ..core import Profile
from ..core import RunStatus, Run, Job, Test

from .tshrag import Tshrag

from ..util.config import Config, CONFIG

from ..util.consts import SYM_TSHRAG
from ..util.consts import PATH_TSHRAG, PATH_DOT_TSHRAG
from ..util.consts import PATH_LOG, PATH_LOCK, PATH_CONFIG
from ..util.consts import TIMEOUT
from ..util.consts import ENCODING



def TshragAPI(tshrag: Tshrag):
    router = APIRouter()

    @router.get("/tests")
    def get_tests():
        return tshrag.list_test()

    @router.get("/test/{test_id}")
    def get_test(test_id: TestId):
        return tshrag.query_test(test_id)

    return router


def MdbAPI(mdb: MetricDB):
    router = APIRouter()

    return router



class Tshragd:
    
    def __init__(self):
        self.root = Path(PATH_TSHRAG)
        self.lock = Lock(self.root / PATH_LOCK, timeout = TIMEOUT)
        self.pool = ThreadPoolExecutor(thread_name_prefix = SYM_TSHRAG)
        self.router = TshragAPI(self.tshrag)
        self.tshrag = Tshrag(
            root = self.root,
            timeout = TIMEOUT,
            encoding = ENCODING,
            config = CONFIG
        )



    def _main(self) -> None:
        while True:
            _tests = [self.tshrag.query_test(id) for id in self.tshrag.list_test()]
            _tests.sort(key = lambda x: x.start_time)
            _machines_ocupied = {
                machine
                for test in _tests
                for machine in test.machine
                if test.status == RunStatus.RUNNING
                or test.status == RunStatus.PREPARING
            }
            _tests_runnable = [
                test
                for test in _tests
                if test.status == RunStatus.PENDING
                and test.start_time < Time.now()
                and test.end_time > Time.now()
                and test.machine.isdisjoint(_machines_ocupied)
            ]
            _tests_to_run = []
            _machines_to_run = set()
            for _test in _tests_runnable:
                if _test.machine.isdisjoint(_machines_to_run):
                    _tests_to_run.append(_test)
                    _machines_to_run.update(_test.machine)
            for _test in _tests_to_run:
                self.pool.submit(
                    self.tshrag.run_test,
                    _test.id,
                )
                Thread(target=self._run, args=(_test.id,))


    def main(self) -> None:
        try:
            self.lock.acquire()
        except Exception as e:
            # TODO: An instance is running
            # TODO: Handle exception
            return
        try:
            self._main()
        except Exception as e:
            # TODO: Handle exception
            pass
        finally:
            self.pool.shutdown()
            self.lock.release()
        return


    def __call__(self):
        self.main()


