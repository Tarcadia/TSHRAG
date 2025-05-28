
# -*- coding: UTF-8 -*-


from typing import List

import os
import shlex
from subprocess import Popen
from ..util import expand_variable



def cmd(
    seqript,
    cmd             : List[str],
):
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    cmd = [expand_variable(c, seqript.env) for c in cmd]
    _proc = Popen(
        args=cmd,
        cwd=str(seqript.cwd),
        env=(os.environ | seqript.env),
    )
    _proc.wait()

