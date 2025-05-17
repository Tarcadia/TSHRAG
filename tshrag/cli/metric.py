
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



def MetricCLI(tshrag: Tshrag) -> click.Group:
    cli = click.Group()
    
    return cli

