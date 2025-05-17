
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

from ..tshrag import Tshrag

from ..util.config import Config

from ..util.consts import SYM_TSHRAG
from ..util.consts import PATH_LOCK
from ..util.consts import TIMEOUT
from ..util.consts import ENCODING
from ..util.consts import CONCURRENCY



def test_main(tshrag: Tshrag, test_id: str) -> None:
    # TODO: Implement distribution
    with tshrag.update_test(test_id) as test:
        test_end_time = test.end_time
        if test.status in Tshrag.RUNSTATUS_POST_TEST:
            return
        elif test.status == RunStatus.PREPARING:
            test.status = RunStatus.RUNNING
        else:
            # TODO: Handle status error
            return
    while Time.now() < test_end_time:
        with tshrag.update_test(test_id) as test:
            test_end_time = test.end_time
            if test.status in Tshrag.RUNSTATUS_POST_TEST:
                return
            elif test.status == RunStatus.RUNNING:
                pass
            else:
                # TODO: Handle status error
                return
        # TODO: Implement execution
        print(f"Test {test_id} is running...")
        time.sleep(TIMEOUT)


