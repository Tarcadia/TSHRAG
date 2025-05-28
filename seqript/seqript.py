
# -*- coding: UTF-8 -*-


from typing import Union, Optional, Generic, TypeVar
from typing import Iterable, Iterator, AsyncIterator
from typing import Tuple, List, Set, Dict, Any
from typing import Callable

from pathlib import Path

from . import engine
from .util import expand_variable_dict



class Seqript:

    _DEFAULT_ENGINES = {
        "nop": engine.nop,
        "seq": engine.seq,
        "par": engine.par,
        "cmd": engine.cmd,
    }

    def __init__(
        self,
        name        : str                   = None,
        cwd         : Path                  = None,
        env         : Dict[str, str]        = None,
        engines     : Dict[str, Callable]   = _DEFAULT_ENGINES,
    ):
        self.name = name
        self.cwd = cwd or Path.cwd()
        self.env = env or dict()
        self.engines = engines or dict()

    def __call__(self, **kwargs):
        _name = kwargs.pop("name", None)
        _cwd = kwargs.pop("cwd", None)
        _env = kwargs.pop("env", None)
        _env = _env and expand_variable_dict(_env, self.env)
        for _k, _call in self.engines.items():
            if _k in kwargs:
                seqript = Seqript(
                    name = f"{self.name}.{_name}" if _name else f"{self.name}.*{_k}",
                    cwd = self.cwd / _cwd if _cwd else self.cwd,
                    env = self.env | _env if _env else self.env,
                    engines = self.engines,
                )
                try:
                    _call(seqript, **kwargs)
                except Exception as e:
                    # TODO: Error handling
                    pass
                return

