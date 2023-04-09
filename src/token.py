from enum import (
    auto,
    Enum,
    unique
)
from typing import (
    Dict,
    NamedTuple
)


@unique
class TokenType(Enum):
    # Keywords
    AND = auto()
    ASSIGN = auto()
    COMMA = auto()
    CONST = auto()
    DIVISION = auto()
    EQUALS = auto()
    ELSE = auto()
    EOF = auto()
    FALSE = auto()
    FUNCTION = auto()
    ILLEGAL = auto()
    GE = auto()
    GT = auto()
    IDENT = auto()
    IF = auto()
    INT = auto()
    INTERSECTION = auto()
    LBRACE = auto()
    LE = auto()
    LET = auto()
    LT = auto()
    LPAREN = auto()
    MINUS = auto()
    MULTIPLICATION = auto()
    NEGATION = auto()
    NOT_EQUALS = auto()
    OR = auto()
    PLUS = auto()
    RBRACE = auto()
    RETURN = auto()
    RPAREN = auto()
    SEMICOLON = auto()
    STRING = auto()
    TRUE = auto()
    UNION = auto()
    VAR = auto()
    XOR = auto()


class Token(NamedTuple):
    # Token: type, literal
    token_type: TokenType
    literal: str

    def __str__(self):
        return f'Type: {self.token_type}, Literal: {self.literal}'


def lookup_token_type(literal: str) -> TokenType:
    # Determine if it is KEYWORD or IDENT
    keywords: Dict[str, TokenType] = {
        'and': TokenType.AND,
        'const': TokenType.CONST,
        'else': TokenType.ELSE,
        'false': TokenType.FALSE,
        'function': TokenType.FUNCTION,
        'if': TokenType.IF,
        'let': TokenType.LET,
        'or': TokenType.OR,
        'return': TokenType.RETURN,
        'true': TokenType.TRUE,
        'var': TokenType.VAR,
        'xor': TokenType.XOR
    }
    return keywords.get(literal, TokenType.IDENT)
