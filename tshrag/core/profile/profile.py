
# -*- coding: UTF-8 -*-


from dataclasses import dataclass



@dataclass
class Profile():
    name            : str
    description     : str
    distribution    : dict
    execution       : dict
    report          : dict

