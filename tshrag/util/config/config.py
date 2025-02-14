
# -*- coding: UTF-8 -*-


from configparser import ConfigParser
from pathlib import Path



class Config(ConfigParser):

    def __init__(self, path:str|Path|None=None):
        super(ConfigParser, self).__init__()
        self.path = path
        if not self.path is None:
            self.read_path(self.path)


    def read_path(self, path:str|Path):
        path = Path(path)
        _configs = []

        if path.is_file():
            _configs = [path]
        if path.is_dir():
            for _root, _, _files in path.walk():
                for _file in _files:
                    _file = _root / _file
                    if _file.suffix.lower() == ".cfg":
                        _configs.append(_file)
        
        _loaded = self.read(_configs)
        for _file in _loaded:
            # TODO: Log file name
            pass

        return self


    def pick_to(self, section:str, obj:object):
        if section in self:
            for _key in self[section]:
                try:
                    _attr = getattr(obj, _key)
                except AttributeError:
                    continue
                _val = type(_attr)(self[section][_key])
                setattr(obj, _key, _val)

