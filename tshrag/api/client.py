# -*- coding: UTF-8 -*-


from typing import AsyncIterable, Iterable
from typing import Tuple, List, Set, Dict, Any

import json
import asyncio
from dataclasses import asdict

import httpx
import websockets

from ..core import Time
from ..core import Identifier, TestId, JobId, DutId
from ..core import MetricKey, MetricInfo, MetricEntry
from ..core import MetricDB

from .metric import UpdateMetricEntry



async def _aiterable(iterable: Iterable) -> AsyncIterable:
    for item in iterable:
        yield item



def update_metric_info(
    test_id         : TestId,
    info            : MetricInfo
):
    # TODO: Fix URL
    _http = httpx.Client(...)
    _test_id = TestId(test_id)
    _resp = _http.post(
        f"/metric/{_test_id}/info",
        json=asdict(info),
    )
    _resp.raise_for_status()
    return MetricInfo(**_resp.json())


def add_metric_entry(
    test_id         : TestId,
    key             : MetricKey,
    entry           : MetricEntry,
    dut             : Set[str]              = None,
):
    # TODO: Fix URL
    _http = httpx.Client(...)
    _test_id = TestId(test_id)
    _key = MetricKey(key)
    _dut = list(dut) if dut else []
    _resp = _http.post(
        f"/metric/{_test_id}/entry",
        params={
            "key": _key,
            "dut": _dut,
        },
        json=asdict(entry),
    )
    _resp.raise_for_status()
    return MetricEntry(**_resp.json())


async def abatch_add_metric_entry(
    test_id         : TestId,
    key             : MetricKey,
    entries         : AsyncIterable[MetricEntry],
    dut             : Set[str]              = None,
):
    _test_id = TestId(test_id)
    _key = MetricKey(key)
    _dut = list(dut) if dut else []
    # TODO: Fix URL
    async with websockets.connect(...) as conn:
        async for entry in entries:
            request = UpdateMetricEntry(
                _key,
                _dut,
                [entry]
            )
            await conn.send(json.dumps(asdict(request), default=str))


def batch_add_metric_entry(
    test_id         : TestId,
    key             : MetricKey,
    entries         : Iterable[MetricEntry],
    dut             : Set[str],
):
    return asyncio.run(
        abatch_add_metric_entry(test_id, key, _aiterable(entries), dut)
    )


