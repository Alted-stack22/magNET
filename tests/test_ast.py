from unittest import TestCase
from src.ast import (
    Identifier,
    LetStatement,
    ReturnStatement,
    Integer,
    Program
)
from src.token import (
    Token,
    TokenType
)


class ASTTest(TestCase):
    def test_let_statement(self) -> None:
        # let item = foo;
        program: Program = Program(statements=[
            LetStatement(
                token=Token(TokenType.LET, literal='let'),
                name=Identifier(Token(TokenType.IDENT, 'item'), 'item'),
                value=Identifier(Token(TokenType.IDENT, 'foo'), 'foo')
            )
        ])
        program_str = str(program)
        self.assertEquals(program_str, 'let item = foo;')

    def test_return_statement(self) -> None:
        # return obj;
        program: Program = Program(statements=[
            ReturnStatement(
                token=Token(TokenType.RETURN, literal='return'),
                return_value=Identifier(Token(TokenType.IDENT, 'obj'), 'obj')
            )
        ])
        program_str = str(program)
        self.assertEquals(program_str, 'return obj')

    def test_integer_statement(self) -> None:
        '''
            let foo = 12;
            return 40;
        '''
        program: Program = Program(statements=[
            LetStatement(
                token=Token(TokenType.LET, literal='let'),
                name=Identifier(Token(TokenType.IDENT, 'foo'), 'foo'),
                value=Identifier(Token(TokenType.INT, '12'), '12')
            ),
            ReturnStatement(
                token=Token(TokenType.RETURN, 'return'),
                return_value=Integer(Token(TokenType.INT, '40'), 40)
            )
        ])
        program_str = str(program)
        self.assertEquals(program_str, 'let foo = 12;return 40')

    # def test_prefix_operator(self) -> None:
        '''
            -2;
            !foo;
            5 + -2;
        '''
