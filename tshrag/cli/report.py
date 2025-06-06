# -*- coding: UTF-8 -*-


from typing import Union, Optional, Generic, TypeVar
from typing import Callable, Generator, Iterable, Iterator, AsyncIterator
from typing import Tuple, List, Set, Dict, Any

import json
from pathlib import Path
from dataclasses import dataclass, asdict, is_dataclass
from subprocess import list2cmdline

import click
from click import Context

from ..core import Time
from ..core import Identifier, TestId, JobId, DutId
from ..core import MetricKey, MetricInfo, MetricEntry
from ..core import MetricDB
from ..core import Profile
from ..core import RunStatus, Run, Job, Test

from ..tshrag import Tshrag

from ..util.consts import TIMEOUT
from ..util.consts import ENCODING



def ReportCLI(tshrag: Tshrag) -> click.Group:
    cli = click.Group()


    @cli.command()
    @click.argument("test-id",              type=TestId)
    @click.option("--start-time", "-t0",    type=Time, default=None)
    @click.option("--end-time", "-t1",      type=Time, default=Time.max)
    @click.option("--output", "-o",         type=click.Path(dir_okay=False), default="report.json")
    def report(
        test_id     : TestId,
        start_time  : Time,
        end_time    : Time,
        output      : str
    ):
        output = Path(output)
        _start_time = Time(start_time)
        _end_time = Time(end_time)
        _report = tshrag.report_test(
            id=test_id,
            start_time=_start_time,
            end_time=_end_time,
        )
        with Path(output).open("w") as f:
            json.dump(asdict(_report), f, indent=4, default=str)
        click.echo(f"Report saved to {output}.")


    return cli

