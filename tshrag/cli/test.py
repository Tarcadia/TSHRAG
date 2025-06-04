
# -*- coding: UTF-8 -*-


from typing import Union, Optional, Generic, TypeVar
from typing import Callable, Generator, Iterable, Iterator, AsyncIterator
from typing import Tuple, List, Set, Dict, Any

import json
from pathlib import Path
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



def _format_test_line(test: Test, header: bool = False) -> str:
    if header:
        return f"{"Test ID":<64} | {"Profile":<24} | {"Start Time":<32} | {"End Time":<32} | {"Status":<16}"
    else:
        return f"{test.id:<64} | {test.profile.name:<24} | {str(test.start_time):<32} | {str(test.end_time):<32} | {test.status.name:<16}"

def _format_test_detail(test: Test) -> str:
    return f"""
    Test ID:    {test.id}
    Profile:    {test.profile.name}
    Start Time: {test.start_time}
    End Time:   {test.end_time}
    Status:     {test.status.name}
    Machine:    {", ".join(test.machine)}
    Device:     {", ".join(test.device)}
    Env:        {", ".join(f"{k}={v}" for k, v in test.env.items())}
    Jobs:       {", ".join(f"{j}" for j in test.jobs)}
    MDB:        {test.mdb}
    """

def _format_job_detail(job: Job) -> str:
    return f"""
    Job ID:     {job.id}
    Start Time: {job.start_time}
    End Time:   {job.end_time}
    Status:     {job.status.name}
    Machine:    {job.machine}
    Device:     {",".join(job.device)}
    Args:       {list2cmdline(job.args)}
    CWD:        {job.cwd}
    Env:        {", ".join(f"{k}={v}" for k, v in job.env.items())}
    PID:        {job.pid}
    Retcode:    {job.retcode}
    """



def TestCLI(tshrag: Tshrag) -> click.Group:
    cli = click.Group()


    @cli.command()
    @click.option("--start-time", "-t0",    type=Time, default=Time.min)
    @click.option("--end-time", "-t1",      type=Time, default=Time.max)
    @click.option("--machine", "-m",        type=str, multiple=True)
    @click.option("--device", "-d",         type=str, multiple=True)
    def list(
        start_time: Time,
        end_time: Time,
        machine: List[str],
        device: List[str],
    ):
        _start_time = Time(start_time)
        _end_time = Time(end_time)
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
        _tests = sorted(_tests, key=lambda x: x.start_time, reverse=True)
        _header = _format_test_line(None, header=True)
        _lines = [_format_test_line(t) for t in _tests]
        click.echo("=" * len(_header))
        click.echo(_header)
        click.echo("-" * len(_header))
        for _l in _lines:
            click.echo(_l)
        click.echo("=" * len(_header))


    @cli.command()
    @click.argument("profile",              type=click.Path(exists=True, dir_okay=False))
    @click.option("--start-time", "-t0",    type=Time, default=None)
    @click.option("--end-time", "-t1",      type=Time, default=Time.max)
    @click.option("--machine", "-m",        type=str, multiple=True)
    @click.option("--device", "-d",         type=str, multiple=True)
    @click.option("--env", "-e",            type=str, multiple=True)
    def create(
        profile: str,
        start_time: Time,
        end_time: Time,
        machine: List[str],
        device: List[str],
        env: List[str],
    ):
        with Path(profile).open("r") as f:
            _profile = Profile(**json.load(f))
        _start_time = Time(start_time)
        _end_time = Time(end_time)
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
        click.echo(_format_test_detail(_test))


    @cli.group()
    @click.argument("test-id", type=TestId)
    @click.pass_context
    def test(
        ctx: Context,
        test_id: TestId,
    ):
        ctx.ensure_object(dict)
        ctx.obj["test-id"] = test_id


    @test.command()
    @click.pass_context
    def detail(
        ctx: Context,
    ):
        test_id = ctx.obj["test-id"]
        test = tshrag.query_test(test_id)
        click.echo(_format_test_detail(test))


    @test.command()
    @click.argument("job-id", type=JobId)
    @click.pass_context
    def job(
        ctx: Context,
        job_id: JobId,
    ):
        test_id = ctx.obj["test-id"]
        job = tshrag.query_job(test_id, job_id)
        click.echo(_format_job_detail(job))


    @test.command()
    @click.option("--start-time", "-t0",    type=Time, default=None)
    @click.option("--end-time", "-t1",      type=Time, default=None)
    @click.option("--duration", "-d",       type=int, default=None)
    @click.pass_context
    def reschedule(
        ctx         : Context,
        start_time  : Optional[Time]        = None,
        end_time    : Optional[Time]        = None,
        duration    : Optional[int]         = None,
    ):
        test_id = ctx.obj["test-id"]
        if(
            tshrag.reschedule_test(
                id=test_id,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
            )
        ):
            click.echo(f"Test {test_id} rescheduled.")
        else:
            click.echo(f"Test {test_id} failed reschedule.")


    @test.command()
    @click.pass_context
    def start(
        ctx: Context
    ):
        test_id = ctx.obj["test-id"]
        if(tshrag.startnow_test(test_id)):
            click.echo(f"Test {test_id} started.")
        else:
            click.echo(f"Test {test_id} failed start.")


    @test.command()
    @click.pass_context
    def stop(
        ctx: Context
    ):
        test_id = ctx.obj["test-id"]
        if(tshrag.stopnow_test(test_id)):
            click.echo(f"Test {test_id} stopped.")
        else:
            click.echo(f"Test {test_id} failed stop.")


    @test.command()
    @click.pass_context
    def cancel(
        ctx: Context
    ):
        test_id = ctx.obj["test-id"]
        if(tshrag.cancel_test(test_id)):
            click.echo(f"Test {test_id} cancelled.")
        else:
            click.echo(f"Test {test_id} failed cancel.")


    return cli

