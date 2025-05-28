
# -*- coding: UTF-8 -*-


from ...util import expand_variable



def comment(
    seqript,
    comment         : str                   = "",
):
    _comment = expand_variable(comment, seqript.env)
    print(f"[{seqript.name}]: {_comment}")


