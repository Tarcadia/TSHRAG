#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


from typing import Union, Optional, Generic, TypeVar
from typing import Callable, Generator, Iterable, Iterator, AsyncIterator
from typing import Tuple, List, Set, Dict, Any

import time
import shlex
from threading import Thread

from pathlib import Path
from contextlib import contextmanager
from dataclasses import asdict
from threading import Thread

import click
from click import Context
from fastapi import FastAPI
from portalocker import Lock

from .tshrag import Tshrag
from .der import distribute
from .der import execute
from .der import report
from .cli import TestCLI
from .cli import MetricCLI
from .cli import ReportCLI
from .cli import InteractiveCLI
from .cli import merge_cli
from .api import TestAPI
from .api import MetricAPI
from .api import MetricWsAPI
from .api import ReportAPI

from .util.consts import SYM_TSHRAG
from .util.consts import TIMEOUT
from .util.consts import ENCODING

from .util.consts import SERVICE_HOST
from .util.consts import SERVICE_PORT

from .util.consts import PATH_DOT_TSHRAG

from .util.config import CONFIG



root = Path(PATH_DOT_TSHRAG)
tshrag = Tshrag(root, distribute=distribute, execute=execute, report=report, config=CONFIG)
daemon_lock = Lock(root / "daemon.lock", timeout=TIMEOUT)

test_api = TestAPI(tshrag)
metric_api = MetricAPI(tshrag)
metric_wsapi = MetricWsAPI(tshrag)
report_api = ReportAPI(tshrag)

test_cli = TestCLI(tshrag)
metric_cli = MetricCLI(tshrag)
report_cli = ReportCLI(tshrag)
interactive_cli = InteractiveCLI(tshrag)



def _main():
    try:
        daemon_lock.acquire()
    except:
        # TODO: Handle existing daemon instance
        print(f"{SYM_TSHRAG} daemon is already running.")
        return
    try:
        import uvicorn
        app = FastAPI()
        app.include_router(test_api, prefix="/api/v1")
        app.include_router(metric_api, prefix="/api/v1")
        app.include_router(metric_wsapi, prefix="/wsapi/v1")
        app.include_router(report_api, prefix="/api/v1")
        app = Thread(
            target=uvicorn.run,
            args=(app,),
            kwargs={
                "host": SERVICE_HOST,
                "port": SERVICE_PORT
            },
            name="API Thread",
            daemon=True,
        )
        app.start()
        while app.is_alive():
            tshrag.refresh()
            time.sleep(TIMEOUT)
    except KeyboardInterrupt:
        return
    finally:
        daemon_lock.release()


def _interactive():
    cli = merge_cli([
        test_cli,
        metric_cli,
        report_cli,
        interactive_cli,
    ])
    while True:
        user_input = click.prompt(SYM_TSHRAG, type=str, prompt_suffix="> ")
        args = shlex.split(user_input)

        if not args:
            continue

        try:
            ctx = cli.make_context(None, args=args)
            cli.invoke(ctx)
        except click.exceptions.Exit:
            continue
        except click.exceptions.Abort:
            break
        except click.exceptions.ClickException as e:
            click.echo(f"Command failed: {e}", err=True)
            click.echo(ctx.get_help(), err=True)
            continue
        except Exception as e:
            click.echo(f"Error occurred: {e}", err=True)
            continue


def _command(args: Tuple[str, ...]):
    cli = merge_cli([
        test_cli,
        metric_cli,
        report_cli,
    ])
    ctx = cli.make_context(SYM_TSHRAG, args=list(args))
    cli.invoke(ctx)



@click.command(context_settings={"ignore_unknown_options": True})
@click.option("--interactive/--command", "-i/-c", is_flag=True, required=False, default=None)
@click.argument("args", type=str, nargs=-1)
@click.pass_context
def main(
    ctx: Context,
    interactive: Optional[bool],
    args: Tuple[str, ...],
):
    if interactive is None:
        _main()
    elif interactive is True:
        _interactive()
    elif interactive is False:
        _command(args)
    else:
        click.echo(f"Invalid option {interactive}. Use --interactive or --command.", err=True)
        ctx.exit()


if __name__ == "__main__":
    main()

