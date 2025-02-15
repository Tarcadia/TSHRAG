
# -*- coding: UTF-8 -*-


from ..consts import ROOT_MACHINE
from ..consts import ROOT_USER
from ..consts import ROOT_CWD
from ..consts import PATH_TSHRAG
from ..consts import PATH_DOT_TSHRAG
from ..consts import PATH_CONFIG

from .config import Config


CONFIG_MACHINE      = None
CONFIG_USER         = None
CONFIG_CWD          = None


if not ROOT_MACHINE is None:
    CONFIG_MACHINE = Config(ROOT_MACHINE / PATH_TSHRAG / PATH_CONFIG)

if not ROOT_USER is None:
    CONFIG_USER = Config(ROOT_USER / PATH_DOT_TSHRAG / PATH_CONFIG)

if not ROOT_CWD is None:
    CONFIG_CWD = Config(ROOT_CWD / PATH_DOT_TSHRAG / PATH_CONFIG)


CONFIG = Config()
CONFIG.update(CONFIG_MACHINE)
CONFIG.update(CONFIG_USER)
CONFIG.update(CONFIG_CWD)

