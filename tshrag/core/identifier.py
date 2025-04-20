
# -*- coding: UTF-8 -*-

import re



class Identifier(str):

    CHARSET = 'abcdefghijklmnopqrstuvwxyz0123456789_'
    
    def __new__(cls, id: str):
        return str.__new__(cls, _format(id, charset=cls.CHARSET))



class TestId(Identifier):
    CHARSET = 'abcdefghijklmnopqrstuvwxyz0123456789_-.'



class JobId(Identifier):
    CHARSET = 'abcdefghijklmnopqrstuvwxyz0123456789_-.'



class DutId(Identifier):
    CHARSET = 'abcdefghijklmnopqrstuvwxyz0123456789_-.'



def _format(id, charset = Identifier.CHARSET):
    _id = str(id).lower()
    _id = ''.join([c for c in _id if c in charset])
    return _id


def split_identifier(str, charset = Identifier.CHARSET):
    _patt = re.compile(rf"[{''.join([re.escape(_c) for _c in charset])}]+")
    return [_format(id, charset) for id in _patt.findall(str)]


def is_identifier(str, charset = Identifier.CHARSET):
    return str == _format(str, charset)

