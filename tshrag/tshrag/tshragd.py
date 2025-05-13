
# -*- coding: UTF-8 -*-


import uuid
import json
import shutil
import time

from pathlib import Path
from threading import Thread
from concurrent.futures import ThreadPoolExecutor

from portalocker import Lock
from fastapi import FastAPI

from ..core import Time
from ..core import Identifier, TestId, JobId, DutId
from ..core import MetricKey, MetricInfo, MetricEntry
from ..core import MetricDB
from ..core import Profile
from ..core import RunStatus, Run, Job, Test

from .tshrag import Tshrag
from .api import TestAPI
from .api import MetricAPI
from .api import ReportAPI

from ..util.config import Config, CONFIG

from ..util.consts import SYM_TSHRAG
from ..util.consts import PATH_TSHRAG, PATH_DOT_TSHRAG
from ..util.consts import PATH_LOG, PATH_LOCK, PATH_CONFIG
from ..util.consts import TIMEOUT
from ..util.consts import ENCODING



class Tshragd:

    REFRESH_INTERVAL = TIMEOUT

    def __init__(self):
        self.root = Path(PATH_TSHRAG)
        self.pool = ThreadPoolExecutor(thread_name_prefix = SYM_TSHRAG)
        self.app = FastAPI(title = SYM_TSHRAG)
        self.tshrag = Tshrag(
            root = self.root,
            timeout = TIMEOUT,
            encoding = ENCODING,
            config = CONFIG
        )

        self.app.include_router(
            TestAPI(self.tshrag),
            prefix = "/api/v1/test",
        )
        self.app.include_router(
            MetricAPI(self.tshrag),
            prefix = "/api/v1/metric",
        )
        self.app.include_router(
            ReportAPI(self.tshrag),
            prefix = "/api/v1/report",
        )


    def main(self) -> None:
        while True:
            self.tshrag.refresh()
            time.sleep(Tshragd.REFRESH_INTERVAL)


    def __call__(self):
        self.main()


