
# -*- coding: UTF-8 -*-

import re



class Id(str):

    ID_CHARS = 'abcdefghijklmnopqrstuvwxyz0123456789_'
    
    def __new__(cls, id: str):
        return str.__new__(cls, _fmt_id(id))


def _fmt_id(id, id_chars = Id.ID_CHARS):
    _id = str(id).lower()
    _id = _id.replace('-', '_')
    _id = ''.join([c for c in _id if c in id_chars])
    return _id


def sub_ids(str, id_chars = Id.ID_CHARS):
    _patt = rf"[{"".join([re.escape(_c) for _c in id_chars])}]+"
    return [_fmt_id(id, id_chars) for id in re.findall(_patt, str)]
