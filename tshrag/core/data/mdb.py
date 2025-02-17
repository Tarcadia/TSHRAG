
# -*- coding: UTF-8 -*-


import json
import shutil

from pathlib import Path
from contextlib import contextmanager
from dataclasses import asdict
from typing import List, Generator

from portalocker import Lock

from .time import Time
from .metric import MetricId
from .metric import MetricIdPattern
from .metric import Metric
from .metric import MetricEntry

from ...util.config import Config
from ...util.consts import PATH_LOCK
from ...util.consts import TIMEOUT
from ...util.consts import ENCODING


class Mdb:

    MDB_FILE_LOCK = PATH_LOCK
    MDB_FILE_MID_SEPARATOR = "-"
    MDB_FILE_INDEX = "index.json"
    MDB_FILE_DATA = "%s.jsonl"
    MDB_TIME_ACCURACY = 12
    MDB_CONFIG_SESSION = "mdb"

    def __init__(
        self, root: Path,
        time_accuracy = MDB_TIME_ACCURACY,
        timeout = TIMEOUT,
        encoding = ENCODING,
        config: Config = None
    ):
        self._root = Path(root)
        self._time_accuracy = time_accuracy
        self._timeout = timeout
        self._encoding = encoding
        if not config is None:
            config.pick_to(Mdb.MDB_CONFIG_SESSION, self)
        
        self._root.mkdir(parents=True, exist_ok=True)


    @contextmanager
    def _metric_lock(self, id: MetricId):
        with Lock(self._get_metric_lock_file(id), timeout=self._timeout) as _l:
            yield _l


    def _get_metric_fsname(self, id: MetricId) -> str:
        return Mdb.MDB_FILE_MID_SEPARATOR.join(id.keys())


    def _get_metric_path(self, id: MetricId) -> Path:
        return self._root / self._get_metric_fsname(id)


    def _get_metric_lock_file(self, id: MetricId) -> Path:
        return self._root / (self._get_metric_fsname(id) + Mdb.MDB_FILE_LOCK)


    def _get_metric_index_file(self, id: MetricId) -> Path:
        return self._get_metric_path(id) / Mdb.MDB_FILE_INDEX


    def _get_metric_data_file(self, id: MetricId, time: Time) -> Path:
        _file = Mdb.MDB_FILE_DATA % str(time)[:self._time_accuracy]
        return self._get_metric_path(id) / _file


    def _glob_metric_index_file(self, pattern: MetricIdPattern) -> Generator[Path, None, None]:
        _file = self._get_metric_path(pattern) / Mdb.MDB_FILE_INDEX
        yield from self._root.glob(_file.relative_to(self._root).as_posix())


    def _glob_metric_data_file(self, id: MetricId) -> Generator[Path, None, None]:
        _file = Mdb.MDB_FILE_DATA % "*"
        yield from self._get_metric_path(id).glob(_file)


    def _range_metric_data_file(self, id: MetricId, start_time: Time, end_time: Time) -> Generator[Path, None, None]:
        _start_time = Time(str(start_time)[:self._time_accuracy])
        _end_time = Time(str(end_time)[:self._time_accuracy])
        for _file in self._glob_metric_data_file(id):
            if not _start_time <= Time(_file.stem) <= _end_time:
                continue
            yield _file


    def create(self, metric: Metric) -> bool:
        with self._metric_lock(metric.id):
            _mpath = self._get_metric_path(metric.id)
            if _mpath.exists():
                return False
            _mpath.mkdir(parents=True, exist_ok=True)
            with self._get_metric_index_file(metric.id).open("w") as fp:
                json.dump(asdict(metric), fp, indent=4)
            return True


    def delete(self, id: MetricId) -> bool:
        id = MetricId(id)
        with self._metric_lock(id):
            _mpath = self._get_metric_path(id)
            if not _mpath.exists():
                return False
            shutil.rmtree(_mpath)
            return True


    def get(self, id: MetricId) -> Metric:
        id = MetricId(id)
        metric = None
        try:
            with self._get_metric_index_file(id).open("r") as fp:
                metric = Metric(**json.load(fp))
        except:
            # TODO: Log error
            pass
        return metric


    def list(self, pattern: MetricIdPattern = MetricIdPattern()) -> List[Metric]:
        pattern = MetricIdPattern(pattern)
        metrics = []
        for _index in self._glob_metric_index_file(pattern):
            try:
                with _index.open("r") as fp:
                    _metric = Metric(**json.load(fp))
            except:
                continue
            if self._get_metric_fsname(_metric.id) == _index.parent.name:
                metrics.append(_metric)
        return metrics


    def read(self, id: MetricId, start_time: Time, end_time: Time) -> List[MetricEntry]:
        id = MetricId(id)
        entries = []
        for _file in self._range_metric_data_file(id, start_time, end_time):
            try:
                with _file.open("r") as fp:
                    for _line in fp:
                        try:
                            _entry = MetricEntry(**json.loads(_line))
                        except:
                            continue
                        if start_time <= _entry.time <= end_time:
                            entries.append(_entry)
            except:
                continue
        entries.sort(key=lambda e : e.time)
        return entries


    def write(self, id: MetricId, entry: MetricEntry) -> bool:
        id = MetricId(id)
        try:
            with self._metric_lock(id):
                with self._get_metric_data_file(id, entry.time).open("a") as fp:
                    fp.write(json.dumps(asdict(entry), default=lambda value : str(value)))
                    fp.write("\n")
            return True
        except:
            return False

