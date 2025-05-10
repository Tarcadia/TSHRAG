
# -*- coding: UTF-8 -*-

from typing import List, Set, Union
from pathlib import Path
import sqlite3

from ..time import Time
from ..identifier import TestId, DutId
from .metric import MetricKey, MetricInfo, MetricEntry



def _dut2strset(dut: Union[DutId, Set[DutId]]) -> Set[str]:
    if dut is None:
        dut = set()
    if isinstance(dut, DutId):
        dut = {dut}
    return {f"#{_d}#" for _d in dut}



class MetricDB:

    def __init__(self, filename: Path):
        self.filename = Path(filename)
        self._init_db()


    def __str__(self) -> str:
        return self.filename.as_posix()


    def _init_db(self):
        with sqlite3.connect(self.filename) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metric_info (
                    key TEXT PRIMARY KEY,
                    name TEXT,
                    description TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metric_entry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test TEXT,
                    dut TEXT,
                    key TEXT,
                    time INTEGER,
                    duration INTEGER,
                    value BLOB
                )
            """)
            conn.commit()


    def list_metric_info(
        self
    ) -> List[MetricInfo]:
        with sqlite3.connect(self.filename) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, name, description FROM metric_info")
            return [MetricInfo(*row) for row in cursor.fetchall()]


    def query_metric_info(
        self,
        key: MetricKey
    ) -> MetricInfo:
        with sqlite3.connect(self.filename) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name, description FROM metric_info WHERE key = ?",
                (str(key),)
            )
            _result = cursor.fetchone()
            if _result is None:
                return MetricInfo(key)
            else:
                return MetricInfo(key, *_result)


    def update_metric_info(
        self,
        info: MetricInfo
    ) -> None:
        with sqlite3.connect(self.filename) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO metric_info VALUES (?, ?, ?)",
                (str(info.key), info.name, info.description)
            )
            conn.commit()


    def query_metric_entry(
        self,
        key: str,
        test: TestId = None,
        dut: Union[DutId, Set[DutId]] = None,
        start_time: Time = None,
        end_time: Time = None,
    ) -> List[MetricEntry]:
        if dut is None:
            dut = set()

        conditions = []
        params = []

        conditions.append("key GLOB ?")
        params.append(key)

        if not test is None:
            conditions.append("test = ?")
            params.append(str(test))
        
        for _d in _dut2strset(dut):
            conditions.append("dut LIKE ? ESCAPE '\\'")
            params.append(f"%{_d.replace("_", "\\_")}%")
        
        if not start_time is None:
            conditions.append("time + duration >= ?")
            params.append(int(start_time))
        
        if not end_time is None:
            conditions.append("time <= ?")
            params.append(int(end_time))
        
        query = f"""
            SELECT time, duration, value 
            FROM metric_entry 
            WHERE {' AND '.join(conditions)}
            ORDER BY time
        """
        
        with sqlite3.connect(self.filename) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [MetricEntry(*row) for row in cursor.fetchall()]


    def add_metric_entry(
        self,
        key: MetricKey,
        entry: MetricEntry,
        test: TestId = None,
        dut: Union[DutId, Set[DutId]] = None,
    ) -> None:
        if test is None:
            test = TestId("")
        if dut is None:
            dut = set()
        
        with sqlite3.connect(self.filename) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO metric_info (key, name, description) VALUES (?, ?, ?)",
                (str(key), "", "")
            )
            cursor.execute(
                "INSERT INTO metric_entry (test, dut, key, time, duration, value) VALUES (?, ?, ?, ?, ?, ?)",
                (str(test), ",".join(_dut2strset(dut)), str(key), int(entry.time), int(entry.duration), entry.value)
            )
            conn.commit()

