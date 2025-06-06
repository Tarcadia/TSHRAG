# -*- coding: UTF-8 -*-


from dataclasses import dataclass



@dataclass
class Profile():
    name            : str
    description     : str
    duration        : int
    distribution    : dict
    execution       : dict
    reporting       : dict

