
# -*- coding: UTF-8 -*-


from typing import Tuple, List, Set, Dict, Any

import re



IDENTIFIER_PLACEHOLDER = re.compile(r"\${(?P<var>[a-zA-Z0-9_]*)}")


def expand_variable(
    s               : str,
    variable        : Dict[str, str],
) -> str:
    return IDENTIFIER_PLACEHOLDER.sub(
        lambda m: variable.get(m.group("var"), "${%s}" % m.group("var")),
        s
    )


def expand_variable_dict(
    d               : Dict[str, str],
    variable        : Dict[str, str],
) -> Dict[str, str]:
    _variable = variable.copy()
    _d = dict()
    for k in d:
        _d[k] = expand_variable(d[k], _variable)
    return _d

