
# -*- coding: UTF-8 -*-


from typing import Union, Optional, Generic, TypeVar
from typing import Callable, Generator, Iterable, Iterator, AsyncIterator
from typing import Tuple, List, Set, Dict, Any

from dataclasses import dataclass
from dataclasses import field, asdict
from functools import lru_cache

from fastapi import APIRouter
from fastapi import Query
from fastapi import WebSocket, WebSocketDisconnect

from ..core import Time
from ..core import Identifier, TestId, JobId, DutId
from ..core import MetricKey, MetricInfo, MetricEntry
from ..core import MetricDB

from ..tshrag import Tshrag

from ..util.consts import SYM_TSHRAG
from ..util.consts import PATH_LOCK
from ..util.consts import TIMEOUT
from ..util.consts import ENCODING
from ..util.consts import CONCURRENCY



@lru_cache(maxsize=CONCURRENCY**2)
def _get_mdb(tshrag: Tshrag, test_id: TestId) -> MetricDB:
    return tshrag.query_test(test_id).get_mdb()



def MetricAPI(tshrag: Tshrag):
    router = APIRouter()


    @router.get("/metric/{test_id}/infos")
    def list_metric_info(
        test_id     : str,
    ):
        _test_id = TestId(test_id)
        _mdb = _get_mdb(tshrag, _test_id)
        _infos = _mdb.list_metric_info()
        return [asdict(_info) for _info in _infos]


    @router.get("/metric/{test_id}/info")
    @router.get("/metric/{test_id}/info/{key}")
    def query_metric_info(
        test_id     : str,
        key         : str,
    ):
        _test_id = TestId(test_id)
        _key = str(key)
        _mdb = _get_mdb(tshrag, _test_id)
        _info = _mdb.query_metric_info(_key)
        return asdict(_info)


    @router.post("/metric/{test_id}/info")
    @router.post("/metric/{test_id}/info/{key}")
    def update_metric_info(
        test_id     : str,
        key         : str,
        info        : Dict,
    ):
        _test_id = TestId(test_id)
        _key = MetricKey(key)
        _mdb = _get_mdb(tshrag, _test_id)
        _info = MetricInfo(key=_key, **info)
        _mdb.update_metric_info(_info)
        return asdict(_info)


    @router.get("/metric/{test_id}/entry")
    @router.get("/metric/{test_id}/entry/{key}")
    def query_metric_entry(
        test_id     : str,
        key         : str,
        dut         : List[str]             = Query([]),
        start_time  : str                   = Query(None),
        end_time    : str                   = Query(None),
    ):
        _test_id = TestId(test_id)
        _key = MetricKey(key)
        _mdb = _get_mdb(tshrag, _test_id)
        _dut = set(dut)
        _start_time = start_time and Time(start_time)
        _end_time = end_time and Time(end_time)
        _entries = _mdb.query_metric_entry(
            key         = _key,
            test        = _test_id,
            dut         = _dut,
            start_time  = _start_time,
            end_time    = _end_time,
        )
        return [asdict(_entry) for _entry in _entries]


    @router.post("/metric/{test_id}/entry")
    @router.post("/metric/{test_id}/entry/{key}")
    def add_metric_entry(
        test_id     : str,
        key         : str,
        entry       : Dict,
        dut         : List[str]             = Query([]),
    ):
        _test_id = TestId(test_id)
        _key = MetricKey(key)
        _mdb = _get_mdb(tshrag, _test_id)
        _dut = set(dut)
        _entry = MetricEntry(**entry)
        _mdb.add_metric_entry(
            key     = _key,
            entry   = _entry,
            test    = _test_id,
            dut     = _dut,
        )
        return asdict(_entry)


    return router



def MetricWsAPI(tshrag: Tshrag):
    router = APIRouter()


    @dataclass
    class MetricEntryUpdate:
        key         : MetricKey
        dut         : List[str]             = field(default_factory=list)
        entries     : List[MetricEntry]     = field(default_factory=list)

        def __post_init__(self):
            self.key = MetricKey(self.key)
            self.dut = list({DutId(d) for d in self.dut})
            self.entries = [
                MetricEntry(**entry)
                if isinstance(entry, dict)
                else entry
                for entry in self.entries
            ]


    @router.websocket("/metric/{test_id}/entry")
    async def add_metric_entry(
        websocket   : WebSocket,
        test_id     : str,
    ):
        _test_id = TestId(test_id)
        _mdb = _get_mdb(tshrag, _test_id)
        await websocket.accept()
        try:
            while True:
                _update = MetricEntryUpdate(**await websocket.receive_json())
                for _entry in _update.entries:
                    _mdb.add_metric_entry(
                        key     = _update.key,
                        entry   = _entry,
                        test    = _test_id,
                        dut     = _update.dut,
                    )
        except WebSocketDisconnect:
            # TODO: Handle disconnection
            pass


    return router


