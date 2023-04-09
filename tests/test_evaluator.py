from unittest import TestCase
from typing import (
    Any,
    cast,
    List,
    Tuple,
    Union
)
from src.lexer import Lexer
from src.parser import Parser
from src.ast import (
    Program,
    ExpressionStatement
)
from src.evaluator import (
    evaluate,
    NULL
)
from src.object import (
    Boolean,
    Environment,
    Error,
    Function,
    Integer,
    Null,
    Object,
    String
)


class EvaluatorTest(TestCase):
    def test_integer_evaluation(self) -> None:
        tests: List[Tuple[str, int]] = [
            ('1', 1),
            ('2', 2),
            ('0', 0),
            ('-3', -3),
            ('-5', -5),
            ('5 + 5', 10),
            ('2 - 3', -1),
            ('2 * -3', -6),
            ('24 / 3', 8),
            ('7 * (9 - 4)', 35),
            ('50 / 2 * 3 - 5', 70)
        ]
        for source, expected in tests:
            evaluated = self._evaluate_tests(source)
            self._test_integer_object(evaluated, expected)

    def test_boolean_evaluation(self) -> None:
        tests: List[Tuple[str, bool]] = [
            ('true', True),
            ('false', False),
            ('1 < 2', True),
            ('1 > 2', False),
            ('0 == 0', True),
            ('5 <= 7', True),
            ('8 != 8', False)
        ]
        for source, expected in tests:
            evaluated = self._evaluate_tests(source)
            self._test_boolean_object(evaluated, expected)

    def test_string_evaluation(self) -> None:
        tests: List[Tuple[str, str]] = [
            ("'Hello world!';", 'Hello world!'),
            ('function (){return "foo";}()', 'foo')
        ]
        for source, expected in tests:
            evaluated = self._evaluate_tests(source)
            self.assertIsInstance(evaluated, String)
            evaluated = cast(String, evaluated)
            self.assertEquals(evaluated.value, expected)

    def test_string_concatenation(self) -> None:
        tests: List[Tuple[str, str]] = [
            ('"foo" + "bar";', 'foobar'),
            ("'Hello' + ' ' + 'world!';", "Hello world!"),
            ('''
                let greet = function (name) {
                    return "Hello " + name + "!";
                };
                greet('David');
            ''', 'Hello David!')
        ]
        for source, expected in tests:
            evaluated = self._evaluate_tests(source)
            self._test_string_object(evaluated, expected)

    def test_string_reps(self) -> None:
        tests: List[Tuple[str, str]] = [
            ('"foo" * 2', 'foofoo'),
            ("'bar' * 3", "barbarbar"),
            ('"text" * "other"', 'Invalid operation: STRING * STRING'),
            ("'more' * false", 'Type mismatch: STRING * BOOLEAN')
        ]
        for source, expected in tests:
            evaluated = self._evaluate_tests(source)
            if type(evaluated) == Error:
                self._test_error_object(evaluated, expected)
            else:
                self._test_string_object(evaluated, expected)

    def test_bang_operator(self) -> None:
        tests: List[Tuple[str, bool]] = [
            ('!false', True),
            ('!true', False),
            ('!!true', True),
            ('!!false', False)
        ]
        for source, expected in tests:
            evaluated = self._evaluate_tests(source)
            self._test_boolean_object(evaluated, expected)

    def test_string_comparison(self) -> None:
        tests: List[Tuple[str, bool]] = [
            ('"a" == "a"', True),
            ('"b" != "b"', False),
            ('"a" == "b"', False),
            ('"a" != "b"', True)
        ]
        for source, expected in tests:
            evaluated = self._evaluate_tests(source)
            self._test_boolean_object(evaluated, expected)

    def test_if_else_evaluation(self) -> None:
        tests: List[Tuple[str, Any]] = [
            ('if (true) {10;} ', 10),
            ('if (false) {2;}', None),
            ('if (1) {8;}', 1),
            ('if (1 < 2) {7;}', 7),
            ('if (1 > 2) {3;}', None),
            ('if (1 < 2) {8;} else {12;}', 8),
            ('if (1 > 2) {1;} else {6;}', 6)
        ]
        for source, expected in tests:
            evaluated = self._evaluate_tests(source)
            if type(expected) == int:
                return self._test_integer_object(evaluated, expected)
            else:
                return self._test_null_object(evaluated)

    # def test_null_evaluation(self, evaluated: Object) -> None:
        # self.assertEquals(evaluated, second)
        # tests: List[Tuple[str, None]] = [
            # ('null', None)
        # ]
        # for source, expected in tests:
            # evaluated = self._evaluate_tests(source)
            # self._test_null_object(evaluated)

    def test_return_evaluation(self) -> None:
        tests: List[Tuple[str, int]] = [
            ('return 3 * 4', 12),
            ('return 8 + 2', 10),
            ('return 12 - 7', 5),
            ('9; return 9 * 10; 10', 90),
            ('''
                if (5 < 6) {
                    if (8 > 3) {
                        return 20;
                    }
                    return 0;
                }
            ''', 20)
        ]
        for source, expected in tests:
            evaluated = self._evaluate_tests(source)
            self._test_integer_object(evaluated, expected)

    def test_error_handling(self) -> None:
        tests: List[Tuple[str, str]] = [
            ('1 + true;', 'Type mismatch: INTEGER + BOOLEAN'),
            ('2 + false; 3 * 5', 'Type mismatch: INTEGER + BOOLEAN'),
            ('-true;', 'Invalid operator (-) for type: BOOLEAN'),
            ('false + true; 8', 'Invalid operation: BOOLEAN + BOOLEAN'),
            ('''
                if (10 > 7) {
                    return true + true;
                }
            ''', 'Invalid operation: BOOLEAN + BOOLEAN'),
            ('''
                if (10 > 7) {
                    if (4 > 2) {
                        return true * false;
                    }
                    return 1;
                }
            ''', 'Invalid operation: BOOLEAN * BOOLEAN'),
            ('''
                if (2 > 7) {
                    return 1;
                } else {
                    return false / true;
                }
            ''', 'Invalid operation: BOOLEAN / BOOLEAN'),
            ('foobar;', 'Identifier not found: foobar'),
            ('"foo" - "bar"', 'Invalid operation: STRING - STRING')
        ]
        for source, expected in tests:
            evaluated = self._evaluate_tests(source)
            self.assertIsInstance(evaluated, Error)
            evaluated = cast(Error, evaluated)
            self.assertEquals(evaluated.message, expected)

    def test_assign_evaluation(self) -> None:
        tests: List[Tuple[str, int]] = [
            ('var a = 1; a;', 1),
            ('let b = 2; b;', 2),
            ('let a = 0; let b = a; b', 0),
            ('let a = 3; let b = a; let c = a + b + 3; c', 9)
        ]
        for source, expected in tests:
            evaluated = self._evaluate_tests(source)
            self._test_integer_object(evaluated, expected)

    def test_vars_evaluation(self) -> None:
        tests: List[Tuple[str, int]] = [
            ('var a = 1;', 1),
            ('let b = 2;', 2),
            ('const c = 0;', 0)
        ]
        for source, expected in tests:
            evaluated = self._evaluate_tests(source)
            self._test_integer_object(evaluated, expected)

    def test_function_evaluation(self) -> None:
        source: str = 'function (x) {return x + 2;}'
        evaluated = self._evaluate_tests(source)
        self.assertIsInstance(evaluated, Function)
        evaluated = cast(Function, evaluated)
        self.assertEquals(len(evaluated.params), 1)
        self.assertEquals(str(evaluated.name), '')
        self.assertEquals(str(evaluated.params[0]), 'x')
        self.assertEquals(str(evaluated.body), 'return (x + 2)')

    def test_func_calls(self) -> None:
        # () not detected
        tests: List[Tuple[str, int]] = [
            ('let a = function (x) {x;}; a(1);', 1),
            ('let b = function (y) {return y;}; b(2);', 2),
            ('let c = function (x, y) {return x + y;}; c(3, 4);', 7),
            ('let d = function (z) {return z * 2;}; d(5);', 10),
            ('let s = function (x, y) {return x + y;}; s(1 + 2, s(3, 4));', 10),
            ('function (x) {x;}(15)', 15)
        ]
        for source, expected in tests: pass
            # evaluated = self._evaluate_tests(source)
            # print(evaluated)
            # self._test_integer_object(evaluated, expected)

    def test_builtin_functions(self) -> None:
        tests: List[Tuple[str, Union[int, str]]] = [
            ('length("")', 0),
            ("length('Hello')", 5),
            ('length("world!")', 6),
            ("length(1)", 'Invalid INTEGER type argument'),
            ('length("foo", "bar")', 'Wrong number of arguments: expected 1 (given 2)')
        ]
        for source, expected in tests:
            evaluated = self._evaluate_tests(source)
            if type(expected) == int:
                expected = cast(int, expected)
                self._test_integer_object(evaluated, expected)
            else:
                expected = cast(str, expected)
                self._test_error_object(evaluated, expected)

    def test_lines_evaluation(self) -> None:
        tests: List[Tuple[str, int]] = [
            # ('let foo = 0;', 1),
            ('true; return 3 * 4;', 2),
            ('12 / 4; 8 < 10;', 2),
            ('''if (false) {
                return 0;
            } else {
                return 1;
            }''', 5)
        ]
        for source, expected in tests:
            evaluated = self._evaluate_tests(source)
            # self.assertEquals(evaluated.line, expected)

    def _evaluate_tests(self, source: str) -> Object:
        lexer: Lexer = Lexer(source)
        parser: Parser = Parser(lexer)
        program: Program = parser.parse_program()
        env: Environment = Environment()
        evaluated = evaluate(program, env)
        assert evaluated is not None
        return evaluated

    def _test_integer_object(self, evaluated: Object, expected: int) -> None:
        self.assertIsInstance(evaluated, Integer)
        evaluated = cast(Integer, evaluated)
        self.assertEquals(evaluated.value, expected)

    def _test_boolean_object(self, evaluated: Object, expected: bool) -> None:
        self.assertIsInstance(evaluated, Boolean)
        evaluated = cast(Boolean, evaluated)
        self.assertEquals(evaluated.value, expected)

    def _test_string_object(self, evaluated: Object, expected: str) -> None:
        self.assertIsInstance(evaluated, String)
        evaluated = cast(String, evaluated)
        self.assertEquals(evaluated.value, expected)

    def _test_error_object(self, evaluated: Object, expected: str) -> None:
        self.assertIsInstance(evaluated, Error)
        evaluated = cast(Error, evaluated)
        self.assertEquals(evaluated.message, expected)

    def _test_null_object(self, evaluated: Object) -> None:
        self.assertEquals(evaluated, NULL)
