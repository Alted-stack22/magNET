from unittest import TestCase
from typing import (
    Any,
    List,
    Tuple,
    Dict,
    Type,
    cast
)
from src.ast import (
    Call,
    Prefix,
    Infix,
    Expression,
    Identifier,
    Integer,
    Boolean,
    If,
    Program,
    Block,
    Function,
    LetStatement,
    ReturnStatement,
    ExpressionStatement,
    StringLiteral
)
from src.lexer import Lexer
from src.parser import Parser


class ParserTest(TestCase):
    def test_parse_program(self) -> None:
        # Return a program
        source: str = 'var x = 5;'
        lexer: Lexer = Lexer(source)
        parser: Parser = Parser(lexer)
        program: Program = parser.parse_program()
        self.assertIsNotNone(program)
        self.assertIsInstance(program, Program)

    def test_let_statements(self) -> None:
        # Review let statements
        source: str = '''
            let x = 5;
            let y = 10;
            let foo = 20 + 5;
        '''
        lexer: Lexer = Lexer(source)
        parser: Parser = Parser(lexer)
        program: Program = parser.parse_program()
        self.assertEquals(len(program.statements), 3)
        for statement in program.statements:
            self.assertEquals(statement.token_literal(), 'let')
            self.assertIsInstance(statement, LetStatement)

    def test_names_in_let_statements(self) -> None:
        # Verify identity tokens
        source: str = '''
            let x = 5;
            let y = 10;
            var foo = 20;
        '''
        lexer: Lexer = Lexer(source)
        parser: Parser = Parser(lexer)
        program: Program = parser.parse_program()
        names: List[str] = []
        expected_names = ['x', 'y', 'foo']
        for statement in program.statements:
            statement = cast(LetStatement, statement)
            assert statement.name is not None
            names.append(statement.name.value)
        self.assertEquals(names, expected_names)

    def test_parse_errors(self) -> None:
        # Check program errors
        source: str = 'let x 5;'
        lexer: Lexer = Lexer(source)
        parser: Parser = Parser(lexer)
        program: Program = parser.parse_program()
        # print(parser.errors)
        self.assertEquals(len(parser.errors), 1)

    def test_return_statement(self) -> None:
        # Review return statements
        source: str = '''
            return 5;
            return foo;
        '''
        lexer: Lexer = Lexer(source)
        parser: Parser = Parser(lexer)
        program: Program = parser.parse_program()
        self.assertEquals(len(program.statements), 2)
        for statement in program.statements:
            self.assertEquals(statement.token_literal(), 'return')
            self.assertIsInstance(statement, ReturnStatement)

    def test_identifier_expression(self) -> None:
        # Verify identifier
        source: str = 'foobar;'
        lexer: Lexer = Lexer(source)
        parser: Parser = Parser(lexer)
        program: Program = parser.parse_program()
        self._test_program_statements(parser, program)
        expression_statement = cast(ExpressionStatement, program.statements[0])
        assert expression_statement.expression is not None
        self._test_literal_expression(
            expression_statement.expression, 'foobar')

    def test_integer_expression(self) -> None:
        # Verify identifier
        source: str = '5;'
        lexer: Lexer = Lexer(source)
        parser: Parser = Parser(lexer)
        program: Program = parser.parse_program()
        self._test_program_statements(parser, program)
        expression_statement = cast(ExpressionStatement, program.statements[0])
        assert expression_statement.expression is not None
        self._test_literal_expression(expression_statement.expression, 5)

    def test_boolean_expression(self) -> None:
        # Verify booleans
        source: str = 'true; false;'
        lexer: Lexer = Lexer(source)
        parser: Parser = Parser(lexer)
        program: Program = parser.parse_program()
        self._test_program_statements(parser, program, 2)
        expected_values: List[bool] = [True, False]
        for statement, expected_value in zip(
                program.statements, expected_values):
            statement = cast(ExpressionStatement, statement)
            assert statement.expression is not None
            self._test_literal_expression(statement.expression, expected_value)

    def test_string_expression(self) -> None:
        source: str = "'Hello world!';"
        lexer: Lexer = Lexer(source)
        parser: Parser = Parser(lexer)
        program: Program = parser.parse_program()
        self._test_program_statements(parser, program)
        expr_stmnt = cast(ExpressionStatement, program.statements[0])
        str_literal = cast(StringLiteral, expr_stmnt.expression)
        self.assertIsInstance(str_literal, StringLiteral)
        self.assertEquals(str_literal.value, 'Hello world!')

    def test_operator_precedence(self) -> None:
        # Verify operators precedence
        test_sources: List[Tuple[str, str, int]] = [
            ('-a * b;', '((- a) * b)', 1),
            ('!-a;', '(! (- a))', 1),
            ('a + b / c', '(a + (b / c))', 1),
            ('3 + 4; -5 * 5', '(3 + 4)((- 5) * 5)', 2),
            ('3 + 8 / 4;', '(3 + (8 / 4))', 1),
            ('1 + (2 + 3) + 4;', '((1 + (2 + 3)) + 4)', 1),
            ('(5 + 2) * 3;', '((5 + 2) * 3)', 1),
            ('-(7 + 6);', '(- (7 + 6))', 1),
            ('(a - b) * d + c', '(((a - b) * d) + c)', 1),
            ('a + sum(b, c) + d', '((a + sum(b, c)) + d)', 1)
        ]
        for source, exp_res, exp_count in test_sources:
            lexer: Lexer = Lexer(source)
            parser: Parser = Parser(lexer)
            program: Program = parser.parse_program()
            self._test_program_statements(parser, program, exp_count)
            # self.assertIsInstance(program.statements[0], ExpressionStatement)
            self.assertEquals(str(program), exp_res)

    def test_tree_operators(self) -> None:
        source: str = '1 + 2 * 3 - 4'
        lexer: Lexer = Lexer(source)
        parser: Parser = Parser(lexer)
        program: Program = parser.parse_program()
        self.assertIsInstance(program, Program)
        self._test_program_statements(parser, program)
        expected_values: List[str] = [
            '((1 + (2 * 3)) - 4)',
            '''(
    (
        1 + (
            2 * 
                3
            )) - 
        4)'''
        ]
        raw_expr = program.statements[0]
        self.assertEquals(str(raw_expr), expected_values[0])
        fmt_expr = cast(ExpressionStatement, raw_expr).format_expr()
        self.assertEquals(fmt_expr, expected_values[1])

    def test_call_expression(self) -> None:
        source: str = 'sum(1, 2 * 3, 20 / 4);'
        lexer: Lexer = Lexer(source)
        parser: Parser = Parser(lexer)
        program: Program = parser.parse_program()
        self._test_program_statements(parser, program)
        call = cast(Call, cast(ExpressionStatement,
                               program.statements[0]).expression)
        self.assertIsInstance(call, Call)
        self._test_identifier(call.func, "sum")
        # Test arguments
        assert call.args is not None
        self.assertEquals(len(call.args), 3)
        self._test_literal_expression(call.args[0], 1)
        self._test_infix_expression(call.args[1], 2, "*", 3)
        self._test_infix_expression(call.args[2], 20, "/", 4)

    def test_if_expression(self) -> None:
        source: str = 'if (x < y) {z;}'
        lexer: Lexer = Lexer(source)
        parser: Parser = Parser(lexer)
        program: Program = parser.parse_program()
        self._test_program_statements(parser, program)
        # Test correct node
        if_expression = cast(
            If,
            cast(
                ExpressionStatement,
                program.statements[0]).expression)
        self.assertIsInstance(if_expression, If)
        # Test condition
        assert if_expression.condition is not None
        self._test_infix_expression(if_expression.condition, 'x', '<', 'y')
        # Test consequence
        assert if_expression.consequence is not None
        self._test_block(if_expression.consequence, ['z'])
        # Test alternative
        self.assertIsNone(if_expression.alternative)

    def test_if_else_expression(self) -> None:
        source: str = 'if (a > b) {c;} else {d;}'
        lexer: Lexer = Lexer(source)
        parser: Parser = Parser(lexer)
        program: Program = parser.parse_program()
        self._test_program_statements(parser, program)
        # Test correct node
        if_expression = cast(
            If,
            cast(
                ExpressionStatement,
                program.statements[0]).expression)
        self.assertIsInstance(if_expression, If)
        # Test condition
        assert if_expression.condition is not None
        self._test_infix_expression(if_expression.condition, 'a', '>', 'b')
        # Test consequence
        assert if_expression.consequence is not None
        self._test_block(if_expression.consequence, ['c'])
        # Test alternative
        assert if_expression.alternative is not None
        self._test_block(if_expression.alternative, ['d'])

    def test_prefix_expression(self) -> None:
        # Verify prefix
        source: str = '-5; !foo; !true;'
        lexer: Lexer = Lexer(source)
        parser: Parser = Parser(lexer)
        program: Program = parser.parse_program()
        self._test_program_statements(parser, program, 3)
        expected_couples: List[Tuple[str, Any]] = [
            ('-', 5), ('!', 'foo'), ('!', True)]
        for statement, (expected_operator, expected_value) in zip(
                program.statements, expected_couples):
            statement = cast(ExpressionStatement, statement)
            self.assertIsInstance(statement.expression, Prefix)
            prefix = cast(Prefix, statement.expression)
            self.assertEquals(prefix.operator, expected_operator)
            assert prefix.right is not None
            self._test_literal_expression(prefix.right, expected_value)

    def test_infix_expressions(self) -> None:
        # Verify suffix
        source: str = '''
            5 + 7;
            12 - 9;
            20 * 2;
            18 / 9;
            3 < 1;
            8 > 2;
            12 == 12;
            34 != 29;
            20 <= 10;
            13 >= 5;
            true ^ false;
            false || true;
            true && true;
        '''
        lexer: Lexer = Lexer(source)
        parser: Parser = Parser(lexer)
        program: Program = parser.parse_program()
        self._test_program_statements(parser, program, 13)
        expected_operators_and_values: List[Tuple[Any, str, Any]] = [
            (5, '+', 7),
            (12, '-', 9),
            (20, '*', 2),
            (18, '/', 9),
            (3, '<', 1),
            (8, '>', 2),
            (12, '==', 12),
            (34, '!=', 29),
            (20, '<=', 10),
            (13, '>=', 5),
            (True, '^', False),
            (False, '||', True),
            (True, '&&', True),
        ]
        for statement, (expected_left, expected_operator, expected_right) in zip(
                program.statements, expected_operators_and_values):
            statement = cast(ExpressionStatement, statement)
            assert statement.expression is not None
            self.assertIsInstance(statement.expression, Infix)
            self._test_infix_expression(
                statement.expression,
                expected_left,
                expected_operator,
                expected_right
            )

    def test_func_literal(self) -> None:
        source: str = 'function sum(a, b) {a + b;}'
        lexer: Lexer = Lexer(source)
        parser: Parser = Parser(lexer)
        program: Program = parser.parse_program()  #! Problems with params
        self._test_program_statements(parser, program)
        # Test correct node type
        func_literal = cast(Function, cast(ExpressionStatement,
                                           program.statements[0]).expression)
        self.assertIsInstance(func_literal, Function)
        # Test name
        self.assertEquals(str(func_literal.name), 'sum')
        # Test params
        self.assertEquals(len(func_literal.params), 2)
        self._test_literal_expression(func_literal.params[0], 'a')
        self._test_literal_expression(func_literal.params[1], 'b')
        # Test body
        assert func_literal.body is not None
        self.assertEquals(len(func_literal.body.statements), 1)
        # rtn_stmnt = cast(ReturnStatement, func_literal.body.statements[0])
        body = cast(ExpressionStatement, func_literal.body.statements[0])
        # assert rtn_stmnt.return_value is not None
        assert body.expression is not None
        # self._test_infix_expression(rtn_stmnt.return_value, 'a', '+', 'b')
        self._test_infix_expression(body.expression, 'a', '+', 'b')

    def _test_func_params(self) -> None:
        tests = [
            {'input': 'function () {}',
             'expected': []},
            {'input': 'function (x) {}',
             'expected': ['x']},
            {'input': 'function (x, y , z) {}',
             'expected': ['x', 'y', 'z']}
        ]
        for test in tests:
            lexer: Lexer = Lexer(str(test['input']))
            parser: Parser = Parser(lexer)
            program: Program = parser.parse_program()
            self._test_program_statements(parser, program)
            func = cast(Function, cast(ExpressionStatement,
                                       program.statements[0]).expression)
            self.assertEquals(len(func.params), len(test['expected']))
            for idx, param in enumerate(test['expected']):
                self._test_literal_expression(func.params[idx], param)

    def _test_infix_expression(
            self,
            expression: Expression,
            expected_left: Any,
            expected_operator: str,
            expected_right: Any) -> None:
        # Check infix expression <src.ast.Expression> (a + b)
        infix = cast(Infix, expression)
        assert infix.left is not None
        self._test_literal_expression(infix.left, expected_left)
        self.assertEquals(infix.operator, expected_operator)
        assert infix.right is not None
        self._test_literal_expression(infix.right, expected_right)

    def _test_program_statements(self,
                                 parser: Parser,
                                 program: Program,
                                 expected_stmnt_count: int = 1) -> None:
        # Check parser, program, statements and errors
        if parser.errors:
            print(parser.errors)
        self.assertEquals(len(parser.errors), 0)
        self.assertEquals(len(program.statements), expected_stmnt_count)
        self.assertIsInstance(program.statements[0], ExpressionStatement)

    def _test_literal_expression(self,
                                 expression: Expression,
                                 expected_value: Any) -> None:
        # Check data type and test expression
        value_type: Type = type(expected_value)
        if value_type == str:
            self._test_identifier(expression, expected_value)
        elif value_type == int:
            self._test_integer(expression, expected_value)
        elif value_type == bool:
            self._test_boolean(expression, expected_value)
        else:
            self.fail(f"Unhandled type of expression. Got={value_type}")

    def _test_identifier(self, expression: Expression,
                         expected_value: str) -> None:
        # Check identifier and expected value
        self.assertIsInstance(expression, Identifier)
        identifier = cast(Identifier, expression)
        self.assertEquals(identifier.value, expected_value)
        self.assertEquals(identifier.token.literal, expected_value)

    def _test_integer(self, expression: Expression,
                      expected_value: int) -> None:
        # Check integer and expected value
        self.assertIsInstance(expression, Integer)
        integer = cast(Integer, expression)
        self.assertEquals(integer.value, expected_value)
        self.assertEquals(integer.token.literal, str(expected_value))

    def _test_boolean(
            self,
            expression: Expression,
            expected_value: bool) -> None:
        # Check boolean and expected value
        self.assertIsInstance(expression, Boolean)
        boolean = cast(Boolean, expression)
        self.assertEquals(boolean.value, expected_value)
        self.assertEquals(
            boolean.token.literal,
            'true' if expected_value else 'false')

    def _test_block(self, block: Block, expected_stmnt: List[str]):
        self.assertIsInstance(block, Block)
        self.assertEquals(len(block.statements), len(expected_stmnt))
        for statement, expected in zip(block.statements, expected_stmnt):
            statement = cast(ExpressionStatement, statement)
            assert statement.expression is not None
            self._test_literal_expression(statement.expression, expected)
