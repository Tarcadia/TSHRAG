
# -*- coding: UTF-8 -*-


import json
import shutil

from pathlib import Path
from dataclasses import asdict
from typing import List, Generator

from portalocker import Lock

from .time import Time
from .metric import MetricId
from .metric import Metric
from .metric import MetricEntry

from ...util.config import Config
from ...util.consts import PATH_LOCK
from ...util.consts import TIMEOUT
from ...util.consts import ENCODING


class Mdb:

    MDB_FILE_MID_SEPARATOR = "-"
    MDB_FILE_INDEX = "index.json"
    MDB_FILE_DATA = "%s.jsonl"
    MDB_TIME_ACCURACY = 12
    MDB_CONFIG_SESSION = "mdb"

    def __init__(self, root: Path, time_accuracy = MDB_TIME_ACCURACY, timeout = TIMEOUT, encoding = ENCODING, config: Config = None):
        self._root = Path(root)
        self._time_accuracy = time_accuracy
        self._timeout = timeout
        self._encoding = encoding
        if not config is None:
            config.pick_to(Mdb.MDB_CONFIG_SESSION, self)
    
    def _get_metric_path(self, id: MetricId) -> Path:
        _subpath = Mdb.MDB_FILE_MID_SEPARATOR.join(id.keys())
        return self._root / _subpath

    def _get_metric_index(self, id: MetricId) -> Path:
        return self._get_metric_path(id) / Mdb.MDB_FILE_INDEX
    
    def _get_metric_file(self, id: MetricId, time: Time) -> Path:
        _file = Mdb.MDB_FILE_DATA % time[:self._time_accuracy]
        return self._get_metric_path(id) / _file
    
    def _glob_metric_file(self, id: MetricId) -> Generator[Path, None, None]:
        _file = Mdb.MDB_FILE_DATA % "*"
        return self._get_metric_path(id).glob(_file)
    
    def _range_metric_file(self, id: MetricId, start_time: Time, end_time: Time) -> Generator[Path, None, None]:
        for _file in self._glob_metric_file(id):
            if not start_time <= Time(_file.stem) <= end_time:
                continue
            yield _file
    
    def _get_metric_lock(self, id: MetricId) -> Path:
        return self._get_metric_path(id) / PATH_LOCK

    def create(self, metric: Metric) -> bool:
        _mpath = self._get_metric_path(metric.id)
        if _mpath.exists():
            return False
        _mpath.mkdir(parents=True, exist_ok=True)
        with Lock(self._get_metric_lock(metric.id), timeout=TIMEOUT):
            with self._get_metric_index(metric.id).open("w") as fp:
                json.dump(asdict(metric), fp, indent=4)
        return True
    
    def delete(self, id: MetricId) -> bool:
        _mpath = self._get_metric_path(id)
        if not _mpath.exists():
            return False
        shutil.rmtree(_mpath)
        return True
    
    def list(self) -> List[Metric]:
        _ids = []
        for _subpath in self._root.iterdir():
            if not _subpath.is_dir():
                continue
            _ids.append(MetricId(*_subpath.name.split(Mdb.MDB_FILE_MID_SEPARATOR)))
        return _ids

    def read(self, id: MetricId, start_time: Time, end_time: Time) -> List[MetricEntry]:
        _entries = []
        with Lock(self._get_metric_lock(id), timeout=self._timeout):
            _index = self._get_metric_index(id)
            if not _index.exists():
                return _entries
            for _file in self._range_metric_file(id, start_time, end_time):
                with _file.open("r") as fp:
                    for _line in fp:
                        if not _line:
                            continue
                        _entry = MetricEntry(**json.loads(_line))
                        if start_time <= _entry.time <= end_time:
                            _entries.append(_entry)
        return _entries

    def write(self, entry: MetricEntry) -> bool:
        with Lock(self._get_metric_lock(entry.id), timeout=self._timeout):
            with self._get_metric_file(entry.id, entry.time).open("a") as fp:
                json.dump(asdict(entry), fp)
                fp.write("\n")

