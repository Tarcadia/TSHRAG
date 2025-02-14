
# -*- coding: UTF-8 -*-


import os
from pathlib import Path

from .project import *


ROOT_MACHINE        = None
ROOT_USER           = None
ROOT_CWD            = None


if os.name == "posix":
    ROOT_MACHINE    = "/etc"
    ROOT_USER       = os.getenv("HOME", None)
    ROOT_CWD        = "."
elif os.name == "nt":
    ROOT_MACHINE    = os.getenv("PROGRAMDATA", None)
    ROOT_USER       = os.getenv("APPDATA", None)
    ROOT_CWD        = "."

if not ROOT_MACHINE is None:
    ROOT_MACHINE    = Path(ROOT_MACHINE)

if not ROOT_USER is None:
    ROOT_USER       = Path(ROOT_USER)

if not ROOT_CWD is None:
    ROOT_CWD        = Path(ROOT_CWD)


PATH_TSHRAG         = SYM_TSHRAG
PATH_DOT_TSHRAG     = f".{SYM_TSHRAG}"

PATH_LOG            = f"{SYM_TSHRAG}.log"
PATH_LOCK           = ".lock"
PATH_CONFIG         = "config"
