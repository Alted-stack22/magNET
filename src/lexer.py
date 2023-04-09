from re import match
from src.token import (
    Token,
    TokenType,
    lookup_token_type
)


class Lexer:
    def __init__(self, source: str) -> None:
        # Read from source and return tokens
        self._source: str = source
        self._character: str = ''
        # Cursor
        self._position: int = 0  # Current character
        self._read_position: int = 0  # Next character
        # First character
        self._read_character()

    def next_token(self) -> Token:
        # Token type analysis
        self._skip_whitespace()
        if match(r'^=$', self._character):
            if self._peek_character() == '=':
                token = self._make_two_character_token(TokenType.EQUALS)
            else:
                token = Token(TokenType.ASSIGN, self._character)
        elif match(r'^!$', self._character):
            if self._peek_character() == '=':
                token = self._make_two_character_token(TokenType.NOT_EQUALS)
            else:
                token = Token(TokenType.NEGATION, self._character)
        elif match(r'^&$', self._character):
            if self._peek_character() == '&':
                token = self._make_two_character_token(TokenType.AND)
            else:
                token = Token(TokenType.INTERSECTION, self._character)
        elif match(r'^\|$', self._character):
            if self._peek_character() == '|':
                token = self._make_two_character_token(TokenType.OR)
            else:
                token = Token(TokenType.UNION, self._character)
        elif match(r'^\^$', self._character):
            token = Token(TokenType.XOR, self._character)
        elif match(r'^\+$', self._character):
            token = Token(TokenType.PLUS, self._character)
        elif match(r'^-$', self._character):
            token = Token(TokenType.MINUS, self._character)
        elif match(r'^\*$', self._character):
            token = Token(TokenType.MULTIPLICATION, self._character)
        elif match(r'^/$', self._character):
            token = Token(TokenType.DIVISION, self._character)
        elif match(r'^$', self._character):
            token = Token(TokenType.EOF, self._character)
        elif match(r'^\($', self._character):
            token = Token(TokenType.LPAREN, self._character)
        elif match(r'^\)$', self._character):
            token = Token(TokenType.RPAREN, self._character)
        elif match(r'^\{$', self._character):
            token = Token(TokenType.LBRACE, self._character)
        elif match(r'^\}$', self._character):
            token = Token(TokenType.RBRACE, self._character)
        elif match(r'^,$', self._character):
            token = Token(TokenType.COMMA, self._character)
        elif match(r'^"|\'$', self._character):
            #* Enable ' " support
            literal = self._read_string()
            return Token(TokenType.STRING, literal)
        elif match(r'^;$', self._character):
            token = Token(TokenType.SEMICOLON, self._character)
        elif match(r'^<$', self._character):
            if self._peek_character() == '=':
                token = self._make_two_character_token(TokenType.LE)
            else:
                token = Token(TokenType.LT, self._character)
        elif match(r'^>$', self._character):
            if self._peek_character() == '=':
                token = self._make_two_character_token(TokenType.GE)
            else:
                token = Token(TokenType.GT, self._character)
        elif self._is_letter(self._character):
            literal = self._read_identifier()
            token_type = lookup_token_type(literal)
            return Token(token_type, literal)
        elif self._is_number(self._character):
            literal = self._read_number()
            return Token(TokenType.INT, literal)
        else:
            token = Token(TokenType.ILLEGAL, self._character)
        self._read_character()
        return token

    def _is_letter(self, character: str) -> bool:
        # Check literal
        return bool(match(r'^[a-zA-Z_]$', character))

    def _is_number(self, character: str) -> bool:
        # Check number
        return bool(match(r'^[0-9]+$', character))

    def _read_character(self) -> None:
        # Read characters (from 0 to EOF)
        if self._read_position >= len(self._source):
            self._character = ''
        else:
            self._character = self._source[self._read_position]
        self._position = self._read_position
        self._read_position += 1

    def _read_identifier(self) -> str:
        # Read the WORD or IDENT
        initial_position = self._position
        while self._is_letter(
                self._character) or self._is_number(
                self._character):
            self._read_character()
        return self._source[initial_position: self._position]

    def _read_number(self) -> str:
        # Read the number
        initial_position = self._position
        while self._is_number(self._character):
            self._read_character()
        return self._source[initial_position: self._position]

    def _read_string(self) -> str:
        quote_type = self._character
        self._read_character()
        initial_position = self._position
        #! while self._character != '\"' or self._character != "\'"
        while self._character != quote_type and \
                self._read_position <= len(self._source):
            self._read_character()
        string = self._source[initial_position: self._position]
        self._read_character()
        return string

    def _skip_whitespace(self) -> None:
        # Skip whitespaces and tabs
        while match(r'^[\s\t]$', self._character):
            self._read_character()

    def _peek_character(self) -> str:
        # Picks up the next character
        if self._read_position >= len(self._source):
            return ''
        return self._source[self._read_position]

    def _make_two_character_token(self, token_type: TokenType) -> Token:
        # Read character and next
        prefix = self._character
        self._read_character()
        suffix = self._character
        # Return token with prefix and suffix
        return Token(token_type, f'{prefix}{suffix}')
