
# -*- coding: UTF-8 -*-


from typing import Union, Optional, Generic, TypeVar
from typing import Callable, Generator, Iterable, Iterator, AsyncIterator
from typing import Tuple, List, Set, Dict, Any

import uuid
import json
import shutil
import time
import os
import subprocess
import threading

from pathlib import Path
from contextlib import contextmanager
from dataclasses import dataclass
from dataclasses import asdict
from threading import Thread

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi import Query
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


@dataclass
class RPopen:
    id              : uuid.UUID
    args            : List[str]
    cwd             : Union[str, Path] = None
    env             : Dict[str, str] = None
    pid             : Optional[int] = None
    retcode         : Optional[int] = None


_processes = {}
_process_lock = threading.Lock()


def _run_process(rpopen: RPopen):
    with open(f"{rpopen.id}.out", "w") as fout, open(f"{rpopen.id}.err", "w") as ferr:
        process = subprocess.Popen(
            rpopen.args,
            cwd=rpopen.cwd,
            env=rpopen.env,
            stdin=subprocess.PIPE,
            stdout=fout,
            stderr=ferr,
            text=True,
            bufsize=1
        )

        rpopen.pid = process.pid
        with _process_lock:
            _processes[rpopen.id] = {
                "rpopen": rpopen,
                "process": process,
                "stdout": fout,
                "stderr": ferr,
            }
        
        process.wait()
        rpopen.retcode = process.returncode


def RPopenAPI():

    router = APIRouter()


    @router.post("/rpopen/", response_model=RPopen)
    async def create_rpopen(
        args: List[str],
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None
    ):
        popen_id = uuid.uuid4()
        rpopen = RPopen(
            id=popen_id,
            args=args,
            cwd=cwd or os.getcwd(),
            env=env or os.environ.copy(),
            pid=None,
            retcode=None
        )
        thread = threading.Thread(target=_run_process, args=(rpopen,))
        thread.daemon = True
        thread.start()
        return rpopen


    @router.get("/rpopen/{popen_id}", response_model=RPopen)
    async def get_rpopen(popen_id: uuid.UUID):
        with _process_lock:
            if popen_id not in _processes:
                raise HTTPException(status_code=404, detail="Process not found")
            return _processes[popen_id]["rpopen"]


    @router.get("/rpopen/{popen_id}/stdout")
    async def get_stdout(popen_id: uuid.UUID):
        with _process_lock:
            if popen_id not in _processes:
                raise HTTPException(status_code=404, detail="Process not found")
            with open(f"{popen_id}.out", "r") as fout:
                return fout.readlines()


    @router.get("/rpopen/{popen_id}/stderr")
    async def get_stderr(popen_id: uuid.UUID):
        with _process_lock:
            if popen_id not in _processes:
                raise HTTPException(status_code=404, detail="Process not found")
            with open(f"{popen_id}.err", "r") as ferr:
                return ferr.readlines()


    @router.post("/rpopen/{popen_id}/stdin")
    async def write_stdin(popen_id: uuid.UUID, content: str):
        with _process_lock:
            if popen_id not in _processes:
                raise HTTPException(status_code=404, detail="Process not found")

            process = _processes[popen_id]["process"]
            if process.stdin and not process.stdin.closed:
                try:
                    process.stdin.write(content + "\n")
                    process.stdin.flush()
                    return {"status": "success"}
                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))
            else:
                raise HTTPException(status_code=400, detail="Process stdin is closed")

    return router


def main():
    import uvicorn
    router = RPopenAPI()
    app = FastAPI(title="RPopenD Process Manager")
    app.include_router(router)
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()

