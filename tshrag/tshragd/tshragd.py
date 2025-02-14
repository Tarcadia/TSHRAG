
# -*- coding: UTF-8 -*-


from typing import List

from ..core import *



def list_tests(start_time: Time, end_time: Time) -> List[Test]:
    pass



def get_test(test_id: str = None) -> Test:
    pass



def get_job(job_id: str) -> Job:
    pass



def list_metrics(test_id: str = None) -> List[Metric]:
    pass



def get_metric(start_time: Time, end_time: Time, metric_id: str, test_id: str = None) -> List[MetricEntry]:
    pass

