from typing import (
    cast,
    Dict,
    List,
    Optional
)
from abc import (
    ABC,
    abstractmethod
)
from enum import (
    auto,
    Enum
)
from src.ast import (
    Block,
    Identifier
)
from src.token import (
    Token,
    TokenType
)
from typing_extensions import Protocol


class ObjectType(Enum):
    BOOLEAN = auto()
    BUILTIN = auto()
    ERROR = auto()
    FUNCTION = auto()
    INTEGER = auto()
    NULL = auto()
    RETURN = auto()
    STRING = auto()


class Object(ABC):
    @abstractmethod
    def type(self) -> ObjectType:
        pass

    @abstractmethod
    def inspect(self) -> str:
        pass


class Integer(Object):
    def __init__(self, value: int) -> None:
        self.value = value

    def type(self) -> ObjectType:
        return ObjectType.INTEGER

    def inspect(self) -> str:
        return str(self.value)


class Boolean(Object):
    def __init__(self, value: bool) -> None:
        self.value = value

    def type(self) -> ObjectType:
        return ObjectType.BOOLEAN

    def inspect(self) -> str:
        return 'true' if self.value else 'false'


class Null(Object):
    def type(self) -> ObjectType:
        return ObjectType.NULL

    def inspect(self) -> str:
        return 'null'


class Return(Object):
    def __init__(self, value: Object) -> None:
        self.value = value

    def type(self) -> ObjectType:
        return ObjectType.RETURN

    def inspect(self) -> str:
        return self.value.inspect()


class Error(Object):
    def __init__(self, message: str, line: int = 1) -> None:
        self.message = message
        self.line = line

    def type(self) -> ObjectType:
        return ObjectType.ERROR

    def inspect(self) -> str:
        return f'[Error] in line {self.line}:\n  {self.message}'


class Environment(Dict):
    def __init__(self, outer = None):
        self._store = dict()
        self._outer = outer

    def __getitem__(self, key):
        try:
            return self._store[key]
        except KeyError as err:
            if self._outer is not None:
                return self._outer[key]
            raise err

    def __setitem__(self, key, value):
        self._store[key] = value

    def __delitem__(self, key):
        del self._store[key]


class Function(Object):
    def __init__(self,
                 params: List[Identifier],
                 body: Block,
                 env: Environment,
                 name: Identifier = Identifier(Token(TokenType.EOF, ''), '')) -> None:
        # Auto inc in repl  ! REPL
        # Save prev params and append in tests  ! PARSER
        self.params = params
        self.body = body
        self.env = env
        self.name = name

    def type(self) -> ObjectType:
        return ObjectType.FUNCTION

    def inspect(self) -> str:
        params: str = ', '.join([str(param) for param in self.params])
        return 'function {}({}) {{\n    {}\n}}'.format(str(self.name), params, str(self.body))


class String(Object):
    def __init__(self, value: str) -> None:
        self.value = value

    def type(self) -> ObjectType:
        return ObjectType.STRING

    def inspect(self) -> str:
        return self.value


class BuiltinFunction(Protocol):
    def __call__(self, *args: Object) -> Object: ...


class Builtin(Object):
    def __init__(self, fn: BuiltinFunction) -> None:
        self.fn = fn

    def type(self) -> ObjectType:
        return ObjectType.BUILTIN

    def inspect(self) -> str:
        return 'builtin function'
