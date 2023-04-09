from unittest import TestCase
from typing import List
from src.token import (
    Token,
    TokenType
)
from src.lexer import Lexer


class LexerTest(TestCase):
    def test_illegals(self) -> None:
        # Illegal characters
        source: str = '¡¿@'
        lexer: Lexer = Lexer(source)
        tokens: List[Token] = []
        for i in range(len(source)):
            tokens.append(lexer.next_token())
            expected_tokens: List[Token] = [
                Token(TokenType.ILLEGAL, '¡'),
                Token(TokenType.ILLEGAL, '¿'),
                Token(TokenType.ILLEGAL, '@')
            ]
        self.assertEquals(tokens, expected_tokens)

    def test_one_character_operators(self) -> None:
        # Operators
        source: str = '=+-*/<>!'
        lexer: Lexer = Lexer(source)
        tokens: List[Token] = []
        for i in range(len(source)):
            tokens.append(lexer.next_token())
        expected_tokens: List[Token] = [
            Token(TokenType.ASSIGN, '='),
            Token(TokenType.PLUS, '+'),
            Token(TokenType.MINUS, '-'),
            Token(TokenType.MULTIPLICATION, '*'),
            Token(TokenType.DIVISION, '/'),
            Token(TokenType.LT, '<'),
            Token(TokenType.GT, '>'),
            Token(TokenType.NEGATION, '!'),
        ]
        self.assertEquals(tokens, expected_tokens)

    def test_eof(self) -> None:
        # End of file
        source: str = '+'
        lexer: Lexer = Lexer(source)
        tokens: List[Token] = []
        for i in range(len(source) + 1):
            tokens.append(lexer.next_token())
        expected_tokens: List[Token] = [
            Token(TokenType.PLUS, '+'),
            Token(TokenType.EOF, '')
        ]
        self.assertEquals(tokens, expected_tokens)

    def test_delimiters(self) -> None:
        # Delimiters
        source: str = '(){},;'
        lexer: Lexer = Lexer(source)
        tokens: List[Token] = []
        for i in range(len(source)):
            tokens.append(lexer.next_token())
        expected_tokens = [
            Token(TokenType.LPAREN, '('),
            Token(TokenType.RPAREN, ')'),
            Token(TokenType.LBRACE, '{'),
            Token(TokenType.RBRACE, '}'),
            Token(TokenType.COMMA, ','),
            Token(TokenType.SEMICOLON, ';')
        ]
        self.assertEquals(tokens, expected_tokens)

    def test_assignment(self) -> None:
        # Read tokens from source (let statement)
        source: str = 'var num_a = 1;'
        lexer: Lexer = Lexer(source)
        tokens: List[Token] = []
        for i in range(5):
            tokens.append(lexer.next_token())
        expected_tokens: List[Token] = [
            Token(TokenType.VAR, 'var'),
            Token(TokenType.IDENT, 'num_a'),
            Token(TokenType.ASSIGN, '='),
            Token(TokenType.INT, '1'),
            Token(TokenType.SEMICOLON, ';')
        ]
        self.assertEquals(tokens, expected_tokens)

    def test_function_declaration(self) -> None:
        # Read tokens from source (lambda function)
        source: str = '''
        var sum = function(a, b) {
            a + b;
        };
        '''
        lexer: Lexer = Lexer(source)
        tokens: List[Token] = []
        for i in range(16):
            tokens.append(lexer.next_token())
        expected_tokens: List[Token] = [
            Token(TokenType.VAR, 'var'),
            Token(TokenType.IDENT, 'sum'),
            Token(TokenType.ASSIGN, '='),
            Token(TokenType.FUNCTION, 'function'),
            Token(TokenType.LPAREN, '('),
            Token(TokenType.IDENT, 'a'),
            Token(TokenType.COMMA, ','),
            Token(TokenType.IDENT, 'b'),
            Token(TokenType.RPAREN, ')'),
            Token(TokenType.LBRACE, '{'),
            Token(TokenType.IDENT, 'a'),
            Token(TokenType.PLUS, '+'),
            Token(TokenType.IDENT, 'b'),
            Token(TokenType.SEMICOLON, ';'),
            Token(TokenType.RBRACE, '}'),
            Token(TokenType.SEMICOLON, ';')
        ]
        self.assertEquals(tokens, expected_tokens)

    def test_function_call(self) -> None:
        # Read tokens from source (return value)
        source: str = 'var res = sum(uno, dos);'
        lexer: Lexer = Lexer(source)
        tokens: List[Token] = []
        for i in range(10):
            tokens.append(lexer.next_token())
        expected_tokens: List[Token] = [
            Token(TokenType.VAR, 'var'),
            Token(TokenType.IDENT, 'res'),
            Token(TokenType.ASSIGN, '='),
            Token(TokenType.IDENT, 'sum'),
            Token(TokenType.LPAREN, '('),
            Token(TokenType.IDENT, 'uno'),
            Token(TokenType.COMMA, ','),
            Token(TokenType.IDENT, 'dos'),
            Token(TokenType.RPAREN, ')'),
            Token(TokenType.SEMICOLON, ';')
        ]
        self.assertEquals(tokens, expected_tokens)

    def test_control_statement(self) -> None:
        # Read tokens from source (if statement)
        source: str = '''
        if (1 < 2) {
            return true;
        }
        else {
            return false;
        }
        '''
        lexer: Lexer = Lexer(source)
        tokens: List[Token] = []
        for i in range(17):
            tokens.append(lexer.next_token())
        expected_tokens: List[Token] = [
            Token(TokenType.IF, 'if'),
            Token(TokenType.LPAREN, '('),
            Token(TokenType.INT, '1'),
            Token(TokenType.LT, '<'),
            Token(TokenType.INT, '2'),
            Token(TokenType.RPAREN, ')'),
            Token(TokenType.LBRACE, '{'),
            Token(TokenType.RETURN, 'return'),
            Token(TokenType.TRUE, 'true'),
            Token(TokenType.SEMICOLON, ';'),
            Token(TokenType.RBRACE, '}'),
            Token(TokenType.ELSE, 'else'),
            Token(TokenType.LBRACE, '{'),
            Token(TokenType.RETURN, 'return'),
            Token(TokenType.FALSE, 'false'),
            Token(TokenType.SEMICOLON, ';'),
            Token(TokenType.RBRACE, '}'),
        ]
        self.assertEquals(tokens, expected_tokens)

    def test_two_character_operator(self) -> None:
        # Check reading double characters
        source: str = '''
            10 == 10;
            10 != 9;
            10 >= 9;
            10 <= 9;
        '''
        lexer: Lexer = Lexer(source)
        tokens: List[Token] = []
        for i in range(16):
            tokens.append(lexer.next_token())
        expected_tokens = [
            Token(TokenType.INT, '10'),
            Token(TokenType.EQUALS, '=='),
            Token(TokenType.INT, '10'),
            Token(TokenType.SEMICOLON, ';'),
            Token(TokenType.INT, '10'),
            Token(TokenType.NOT_EQUALS, '!='),
            Token(TokenType.INT, '9'),
            Token(TokenType.SEMICOLON, ';'),
            Token(TokenType.INT, '10'),
            Token(TokenType.GE, '>='),
            Token(TokenType.INT, '9'),
            Token(TokenType.SEMICOLON, ';'),
            Token(TokenType.INT, '10'),
            Token(TokenType.LE, '<='),
            Token(TokenType.INT, '9'),
            Token(TokenType.SEMICOLON, ';')
        ]
        self.assertEquals(tokens, expected_tokens)

    def test_string(self) -> None:
        source: str = '''
            'foo';
            "Hello world!";
        '''
        lexer: Lexer = Lexer(source)
        tokens: List[Token] = []
        for i in range(4):
            tokens.append(lexer.next_token())
        expected_tokens = [
            Token(TokenType.STRING, 'foo'),
            Token(TokenType.SEMICOLON, ';'),
            Token(TokenType.STRING, 'Hello world!'),
            Token(TokenType.SEMICOLON, ';')
        ]
        self.assertEquals(tokens, expected_tokens)
