
# -*- coding: UTF-8 -*-


from typing import List



def seq(
    seqript,
    seq             : List,
):
    for _task in seq:
        seqript(**_task)

