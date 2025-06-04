# -*- coding: UTF-8 -*-


from types import NoneType
from typing import Union, Optional, Generic, TypeVar, ForwardRef
from typing import Callable, Generator, Iterable, Iterator, AsyncIterator
from typing import Tuple, List, Set, Dict, Any
from typing import get_type_hints, get_origin, get_args

from enum import Enum
from dataclasses import dataclass, asdict, is_dataclass
from datetime import datetime
from contextlib import suppress
from pathlib import Path



def Schema(T):

    _schematicating = dict()
    _schematicated = dict()

    def _dataclass(T, v):
        _h = get_type_hints(T, localns=_schematicated)
        _f = {
            _k: _constructor(_t)(v.get(_k))
            for _k, _t in _h.items()
            if _k in v
        }
        return T(**_f)

    def _Union(*T, v):
        for t in T:
            with suppress(TypeError, ValueError):
                return _constructor(t)(v)
        raise ValueError(f"Expected one of {T}, got {type(v)} with value {v}.")

    def _List(T0, v):
        if isinstance(v, list):
            return [
                _constructor(T0)(i)
                for i in v
            ]
        else:
            raise ValueError(f"Expected a list, got {type(v)} with type {T0}.")

    def _Dict(T0, T1, v):
        if isinstance(v, dict):
            return {
                _constructor(T0)(k) : _constructor(T1)(i)
                for k, i in v.items()
            }
        else:
            raise ValueError(f"Expected a dict, got {type(v)} with types {T0} and {T1}.")

    def _list(v):
        if isinstance(v, list):
            return list(v)
        else:
            raise ValueError(f"Expected a list, got {type(v)}.")

    def _dict(v):
        if isinstance(v, dict):
            return {
                str(k) : i
                for k, i in v.items()
            }
        else:
            raise ValueError(f"Expected a dict, got {type(v)}.")

    def _enum(v):
        if isinstance(v, Enum):
            return v
        else:
            raise ValueError(f"Expected an Enum, got {type(v)}.")

    def _path(v):
        if isinstance(v, Path):
            return v.as_posix()
        else:
            raise ValueError(f"Expected a Path, got {type(v)}.")

    def _any(v):
        return v

    def _none(v):
        if v is None:
            return None
        else:
            raise ValueError("Expected None, got something else.")


    def _constructor(T):
        if isinstance(T, ForwardRef):
            if T.__forward_arg__ in _schematicated:
                return _constructor(_schematicated[T.__forward_arg__])
            else:
                raise TypeError(f"Forward reference {T.__forward_arg__} is not defined in the schema context.")
        elif is_dataclass(T):
            return lambda v : _dataclass(T, v)
        elif get_origin(T) in (Union,):
            targs = get_args(T)
            return lambda v : _Union(*targs, v=v)
        elif get_origin(T) in (list, List):
            targs = get_args(T)
            return lambda v : _List(*targs, v=v)
        elif get_origin(T) in (dict, Dict):
            targs = get_args(T)
            return lambda v : _Dict(*targs, v=v)
        elif issubclass(T, list):
            return _list
        elif issubclass(T, dict):
            return _dict
        elif issubclass(T, Enum):
            return _enum
        elif issubclass(T, Path):
            return _path
        elif issubclass(T, int):
            return int
        elif issubclass(T, float):
            return float
        elif issubclass(T, str):
            return str
        elif T is Any:
            return _any
        elif T is NoneType:
            return _none
        else:
            raise TypeError(f"Unconstructable type: {T}")


    def _schematicate(T):
        if is_dataclass(T):
            if T.__name__ in _schematicating and _schematicating[T.__name__] is not T:
                raise TypeError(f"Type {T} has a name conflict in the schema context: {T.__name__}.")
            elif T.__name__ in _schematicating and _schematicating[T.__name__] is T:
                return _schematicated[T.__name__]
            _schematicating[T.__name__] = T
            _schematicated[T.__name__] = T.__name__
            _hints = get_type_hints(T)
            _schema = dataclass(
                type(
                    T.__name__,
                    (),
                    {"__annotations__": {
                        field_name: _schematicate(field_type)
                        for field_name, field_type in _hints.items()
                    }},
                )
            )
            _schematicated[T.__name__] = _schema
            return _schema
        elif get_origin(T) in (Iterable, set, Set, tuple, Tuple, list, List):
            targs = get_args(T)
            return List[Union[tuple(_schematicate(_t) for _t in targs)]]
        elif get_origin(T) in (dict, Dict):
            targs = get_args(T)
            return Dict[tuple(_schematicate(_t) for _t in targs)]
        elif get_origin(T) in (Union,):
            targs = get_args(T)
            return Union[tuple(_schematicate(_t) for _t in targs)]
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
        elif T is Any:
            return Any
        elif T is NoneType:
            return NoneType
        else:
            raise TypeError(f"Unschematicable type: {T}")


    def _coremixin(T):
        class _CoreMixin:

            def tocore(self, **kwargs):
                return T(**kwargs, **asdict(self))

            @classmethod
            def fromcore(cls, obj, **kwargs):
                _fields = {} if obj is None else asdict(obj)
                _fields |= kwargs
                return _constructor(cls)(_fields)

        return _CoreMixin

    return type(
        T.__name__,
        (_schematicate(T), _coremixin(T)),
        {},
    )

