from typing import (
    cast,
    Dict
)
from src.object import (
    Builtin,
    Error,
    Integer,
    Object,
    String
)


_UNSUPPORTED_ARG_TYPE = 'Invalid {} type argument'
_WRONG_ARGS_NUM = 'Wrong number of arguments: expected {} (given {})'


def length(*args: Object) -> Object:
    if len(args) != 1:
        return Error(_WRONG_ARGS_NUM.format(1, len(args)))
    elif type(args[0]) == String:
        arg = cast(String, args[0])
        return Integer(len(arg.value))
    else:
        return Error(_UNSUPPORTED_ARG_TYPE.format(args[0].type().name))
    return Integer(1)

BUILTINS: Dict[str, Builtin] = {
    'length': Builtin(fn=length)
    # '': Builtin(fn=)
}
