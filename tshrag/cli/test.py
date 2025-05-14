
# -*- coding: UTF-8 -*-


import click

from ..core import Time
from ..core import Identifier, TestId, JobId, DutId
from ..core import MetricKey, MetricInfo, MetricEntry
from ..core import MetricDB
from ..core import Profile
from ..core import RunStatus, Run, Job, Test

from ..tshrag import Tshrag



def TestCLI(tshrag: Tshrag):
    cli = click.Group(name="test")

    @cli.command(name="list")
    def list():
        print(tshrag.list_test())

    return cli

