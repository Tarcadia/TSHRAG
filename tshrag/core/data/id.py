
# -*- coding: UTF-8 -*-



class Id(str):

    ID_CHARS = 'abcdefghijklmnopqrstuvwxyz0123456789_'
    
    def __new__(cls, id: str):
        _id = str(id).lower()
        _id = _id.replace('-', '_')
        _id = ''.join([c for c in _id if c in cls.ID_CHARS])
        return str.__new__(cls, _id)

