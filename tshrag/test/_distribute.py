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
from threading import Thread

import seqript.seqript
import seqript.engine
import seqript.engine.contrib
from seqript.seqript import Seqript

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

from ..util.consts import ENV_PREFIX
from ..util.consts import ENV_HOST
from ..util.consts import ENV_TEST_ID
from ..util.consts import ENV_TEST_MACHINE
from ..util.consts import ENV_TEST_DEVICE
from ..util.consts import ENV_TEST_DIR
from ..util.consts import ENV_JOB_ID
from ..util.consts import ENV_JOB_MACHINE
from ..util.consts import ENV_JOB_DEVICE
from ..util.consts import ENV_JOB_DIR



def distribute(
    tshrag          : Tshrag,
    test_id         : TestId,
    host            : str,
) -> None:
    test = tshrag.query_test(test_id)
    distributions = []
    for machine in test.machine:
        _seqript = Seqript(
            name = f"{test_id}-distribution-{machine}",
            cwd = Path() / test_id / "distribution" / machine,
            env = {
                ENV_HOST: host,
                ENV_TEST_ID: test_id,
                ENV_TEST_MACHINE: ";".join(test.machine),
                ENV_TEST_DEVICE: ";".join(test.device),
                ENV_JOB_MACHINE: machine,
                ENV_JOB_DEVICE: ";".join(test.device),
            },
            engines = Seqript._DEFAULT_ENGINES | {
                "web" : None
            },
        )
        _thread = Thread(
            target  = _seqript,
            kwargs  = test.profile.distribution,
            name    = f"{SYM_TSHRAG}-{_seqript.name}",
            daemon  = False,
        )
        distributions.append(_thread)
        _thread.start()

    for _thread in distributions:
        _thread.join()
    # TODO: Implement distribution
    pass


