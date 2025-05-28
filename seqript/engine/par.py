
# -*- coding: UTF-8 -*-


from typing import List

from threading import Thread



def par(
    seqript,
    par             : List,
):
    threads = [Thread(target=seqript, kwargs=_task) for _task in par]
    for _thread in threads:
        _thread.start()
    for _thread in threads:
        _thread.join()

