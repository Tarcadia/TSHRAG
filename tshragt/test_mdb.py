
# -*- coding: UTF-8 -*-


import shutil

from datetime import datetime
from tshrag import Time
from tshrag import Metric, MetricEntry
from tshrag import Mdb


test_value_1 = "test::value::1"

def test():
    m = Metric(
        id=test_value_1,
        name="Test Value 1",
        type="m",
        description="This is Test Value 1 description."
    )

    try:
        shutil.rmtree(".mdb")
    except:
        pass
    mdb = Mdb(".mdb")

    e0 = MetricEntry("now", value="xxx")
    e1 = MetricEntry(Time(), value=1234)
    e2 = MetricEntry(None, value=None)
    e3 = MetricEntry(datetime.now(), float("inf"))
    entries = [e0, e1, e2, e3]
    entries.sort(key=lambda e : e.time)

    for i in range(100):
        assert mdb.create(m)

        assert mdb.write(test_value_1, e0)
        assert mdb.write(test_value_1, e1)
        assert mdb.write(test_value_1, e2)
        assert mdb.write(test_value_1, e3)

        assert mdb.list() == [m]
        assert mdb.get(test_value_1) == m
        assert mdb.read(test_value_1, Time.min, Time.max) == entries
        assert mdb.read(test_value_1, Time.max, Time.min) == []
        assert mdb.delete(test_value_1)
        assert mdb.get(test_value_1) is None
        assert mdb.read(test_value_1, Time.min, Time.max) == []


if __name__ == "__main__":
    test()

