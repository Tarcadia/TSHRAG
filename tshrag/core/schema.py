
# -*- coding: UTF-8 -*-


from types import NoneType
from typing import Union, Iterable, Tuple, List, Set, Dict, Any
from typing import get_type_hints, get_origin, get_args

from enum import Enum
from dataclasses import dataclass, asdict, is_dataclass
from datetime import datetime
from pathlib import Path



def _constructor(T):
    if is_dataclass(T):
        return lambda v : T(**v)
    elif get_origin(T) in (list, List):
        targs = get_args(T)
        return lambda v : [
            _constructor(targs[0])(i)
            for i in v
        ]
    elif get_origin(T) in (dict, Dict):
        targs = get_args(T)
        return lambda v : {
            _constructor(targs[0])(k) : _constructor(targs[1])(i)
            for k, i in v.items()
        }
    elif issubclass(T, list):
        return lambda v : v
    elif issubclass(T, dict):
        return lambda v : {
            str(k) : i
            for k, i in v.items()
        }
    elif issubclass(T, Enum):
        return lambda v : v
    elif issubclass(T, Path):
        return lambda v : v.as_posix()
    elif issubclass(T, int):
        return int
    elif issubclass(T, float):
        return float
    elif issubclass(T, str):
        return str
    elif issubclass(T, Any):
        return lambda v : v
    elif issubclass(T, NoneType):
        return lambda v : None
    else:
        raise TypeError(f"Unconstructable type: {T}")


def _schematicate(T):
    if is_dataclass(T):
        _hints = get_type_hints(T)
        _schema = type(
            T.__name__,
            (),
            {"__annotations__": {
                field_name: _schematicate(field_type)
                for field_name, field_type in _hints.items()
            }},
        )
        return dataclass(_schema)
    elif get_origin(T) in (Iterable, set, Set, tuple, Tuple, list, List):
        targs = get_args(T)
        return List[*(_schematicate(_t) for _t in targs)]
    elif get_origin(T) in (dict, Dict):
        targs = get_args(T)
        return Dict[*(_schematicate(_t) for _t in targs)]
    elif get_origin(T) in (Union,):
        targs = get_args(T)
        return _schematicate(targs[0])
    elif issubclass(T, (set, tuple, list)):
        return list
    elif issubclass(T, (dict,)):
        return dict
    elif issubclass(T, Enum):
        return T
    elif issubclass(T, Path):
        return T
    elif issubclass(T, datetime):
        return str
    elif issubclass(T, int):
        return int
    elif issubclass(T, float):
        return float
    elif issubclass(T, str):
        return str
    elif issubclass(T, Any):
        return Any
    elif issubclass(T, NoneType):
        return NoneType
    else:
        raise TypeError(f"Unschematicable type: {T}")


def _coremixin(T):
    class _CoreMixin:

        def tocore(self, **kwargs):
            return T(**kwargs, **asdict(self))

        @classmethod
        def fromcore(cls, obj, **kwargs):
            _hints = get_type_hints(cls)
            _fields = asdict(obj) | kwargs
            _fields = {
                field_name: _constructor(field_type)(_fields.get(field_name))
                for field_name, field_type in _hints.items()
            }
            return cls(**_fields)

    return _CoreMixin


def Schema(T):
    return type(
        T.__name__,
        (_schematicate(T), _coremixin(T)),
        {},
    )

