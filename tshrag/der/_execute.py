# -*- coding: UTF-8 -*-


from typing import Union, Optional, Generic, TypeVar
from typing import Callable, Generator, Iterable, Iterator, AsyncIterator
from typing import Tuple, List, Set, Dict, Any

import uuid
import json
import shutil
import time
import os
import shlex

from pathlib import Path
from threading import Thread
from subprocess import Popen

import seqript.seqript
import seqript.engine
import seqript.engine.contrib
from seqript.seqript import Seqript
from seqript.util import expand_variable, expand_variable_dict

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



def _engine_cmd(
    tshrag          : Tshrag,
    test_id         : TestId,
    job_machine     : DutId,
    job_device      : List[DutId],
) -> Callable[[Seqript, List[str]], None]:

    def cmd(
        seqript     : Seqript,
        cmd         : List[str],
    ):
        if isinstance(cmd, str):
            cmd = shlex.split(cmd)
        job = tshrag.create_job(
            test_id = test_id,
            job_prefix = seqript.name,
        )
        job_id = job.id
        cwd = seqript.cwd.as_posix()
        env = seqript.env | {
            ENV_JOB_ID: job_id,
            ENV_JOB_MACHINE: job_machine,
            ENV_JOB_DEVICE: ";".join(job_device),
            ENV_JOB_DIR: cwd
        }
        cmd = [
            expand_variable(c, env)
            for c in cmd
        ]
        with tshrag.update_job(test_id, job_id) as job:
            job.machine = job_machine
            job.device  = job_device
            job.args    = cmd
            job.cwd     = cwd
            job.env     = env
        
        with tshrag.update_job(test_id, job_id) as job:
            job.status = RunStatus.RUNNING
            job.start_time = Time.now()
            try:
                proc = Popen(
                    args=job.args,
                    cwd=job.cwd,
                    env=(os.environ | job.env),
                )
                job.pid = proc.pid
            except Exception as e:
                job.status = RunStatus.CRASHED
                job.pid = None
                job.retcode = None
                return

        proc.wait()
        with tshrag.update_job(test_id, job_id) as job:
            job.end_time = Time.now()
            job.retcode = proc.returncode
            if proc.returncode:
                job.status = RunStatus.CRASHED
            else:
                job.status = RunStatus.COMPLETED

    return cmd


def execute(
    tshrag          : Tshrag,
    test_id         : str,
) -> None:
    test = tshrag.query_test(test_id)
    executions = []
    for machine in test.machine:
        _seqript = Seqript(
            name = f"{test_id}-execution-{machine}",
            cwd = Path() / test_id / "execution" / machine,
            env = test.env | {
                ENV_HOST: tshrag._host,
                ENV_TEST_ID: test_id,
                ENV_TEST_MACHINE: ";".join(test.machine),
                ENV_TEST_DEVICE: ";".join(test.device),
            },
            engines = Seqript._DEFAULT_ENGINES | {
                "cmd"   : _engine_cmd(tshrag, test_id, machine, test.device),
                "sleep" : seqript.engine.contrib.sleep,
                "comment": seqript.engine.contrib.comment,
            },
        )
        _thread = Thread(
            target  = _seqript,
            kwargs  = test.profile.execution,
            name    = f"{SYM_TSHRAG}-{_seqript.name}",
            daemon  = False,
        )
        executions.append(_thread)
        _thread.start()

    for _thread in executions:
        _thread.join()

    return

