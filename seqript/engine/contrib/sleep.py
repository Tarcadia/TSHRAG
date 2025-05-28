
# -*- coding: UTF-8 -*-


import time

from ...util import expand_variable



def sleep(
    seqript,
    sleep           : int                   = 0,
):
    if isinstance(sleep, str):
        sleep = expand_variable(sleep, seqript.env)
        sleep = int(sleep)
    print(f"[{seqript.name}]: Start sleep {sleep}s.")
    time.sleep(sleep)
    print(f"[{seqript.name}]: Done sleep {sleep}s.")


