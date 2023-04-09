from typing import (
    Any,
    cast,
    List,
    Optional,
    Type
)
from src.builtins import BUILTINS
import src.ast as ast
from src.object import (
    Boolean,
    Builtin,
    Environment,
    Error,
    Function,
    Integer,
    Null,
    Object,
    ObjectType,
    Return,
    String
)


TRUE = Boolean(True)
FALSE = Boolean(False)
NULL = Null()

_NOT_A_FUNCTION = 'Not a function: {}'
_TYPE_MISMATCH = 'Type mismatch: {} {} {}'
_UNKNOWN_PREFIX_OPER = 'Invalid operator ({}) for type: {}'
_UNKNOWN_INFIX_OPER = 'Invalid operation: {} {} {}'
_UNKNOWN_IDENT = 'Identifier not found: {}'


def _evaluate_program(program: ast.Program, env: Environment) -> Optional[Object]:
    res: Optional[Object] = None
    for stmnt in program.statements:
        res = evaluate(stmnt, env)
        if type(res) == Return:
            res = cast(Return, res)
            return res.value
        elif type(res) == Error:
            return res
    return res


def _ext_func_env(fn: Function, args: List[Object]) -> Environment:
    env = Environment(outer=fn.env)
    for idx, param in enumerate(fn.params):
        env[param.value] = args[idx]
    return env


def _unwrap_return_value(obj: Object) -> Object:
    if type(obj) == Return:
        obj = cast(Return, obj)
        return obj.value
    return obj


def _apply_func(fn: Object, args: List[Object]) -> Object:
    if type(fn) == Function:
        fn = cast(Function, fn)
        ext_env = _ext_func_env(fn, args)
        evaluated = evaluate(fn.body, ext_env)
        assert evaluated is not None
        return _unwrap_return_value(evaluated)
    elif type(fn) == Builtin:
        fn = cast(Builtin, fn)
        return fn.fn(*args)
    else:
        return _new_error(_NOT_A_FUNCTION, [fn.type().name])

def _evaluate_expr(expressions: List[ast.Expression], env: Environment) -> List[Object]:
    res: List[Object] = []
    for expression in expressions:
        evaluated = evaluate(expression, env)
        assert evaluated is not None
        res.append(evaluated)
    return res


def _evaluate_infix_expr(operator: str,
                         left: Object,
                         right: Object) -> Object:
    if left.type() == ObjectType.INTEGER \
            and right.type() == ObjectType.INTEGER:
        return _eval_infix_int(operator, left, right)
    elif left.type() == ObjectType.STRING \
            and (right.type() == ObjectType.STRING or right.type() == ObjectType.INTEGER):
        return _eval_infix_str(operator, left, right)
    elif operator == '==':
        return _to_boolean_object(left is right)
    elif operator == '!=':
        return _to_boolean_object(left is not right)
    elif left.type() != right.type():
        return _new_error(_TYPE_MISMATCH, [left.type().name,
                                           operator,
                                           right.type().name])
    else:
        return _new_error(_UNKNOWN_INFIX_OPER, [left.type().name,
                                                operator,
                                                right.type().name])


def _eval_infix_int(operator: str, left: Object, right: Object):
    left_val = cast(Integer, left).value
    right_val = cast(Integer, right).value
    if operator == '+':
        return Integer(left_val + right_val)
    elif operator == '-':
        return Integer(left_val - right_val)
    elif operator == '*':
        return Integer(left_val * right_val)
    elif operator == '/':
        return Integer(left_val // right_val)
    elif operator == '<':
        return _to_boolean_object(left_val < right_val)
    elif operator == '>':
        return _to_boolean_object(left_val > right_val)
    elif operator == '==':
        return _to_boolean_object(left_val == right_val)
    elif operator == '!=':
        return _to_boolean_object(left_val != right_val)
    elif operator == '<=':
        return _to_boolean_object(left_val <= right_val)
    elif operator == '>=':
        return _to_boolean_object(left_val >= right_val)
    else:
        return _new_error(_UNKNOWN_INFIX_OPER, [left.type().name,
                                                operator,
                                                right.type().name])


def _eval_infix_str(operator: str, left: Object, right: Object) -> Object:
    left_val = cast(String, left).value
    if right.type() == ObjectType.STRING:
        right_val = cast(String, right).value
        if operator == '+':
            return String(left_val + right_val)
        elif operator == '==':
            return _to_boolean_object(left_val == right_val)
        elif operator == '!=':
            return _to_boolean_object(left_val != right_val)
        else:
            return _new_error(_UNKNOWN_INFIX_OPER, [left.type().name,
                                                    operator,
                                                    right.type().name])
    if right.type() == ObjectType.INTEGER and operator == '*':
        times = cast(Integer, right).value
        return String(left_val * times)
    else:
        return _new_error(_TYPE_MISMATCH, [left.type().name,
                                           operator,
                                           right.type().name])


def _evaluate_prefix_expr(operator: str, right: Object) -> Object:
    if operator == '!':
        return _evaluate_bang(right)
    elif operator == '+':
        return _evaluate_positive(right)
    elif operator == '-':
        return _evaluate_negative(right)
    else:
        return _new_error(_UNKNOWN_PREFIX_OPER, [operator, right.type().name])


def _evaluate_block_statements(block: ast.Block, env: Environment) -> Optional[Object]:
    res: Optional[Object] = None
    for stmnt in block.statements:
        res = evaluate(stmnt, env)
        if res is not None and \
                (res.type() == ObjectType.RETURN or res.type() == ObjectType.ERROR):
            return res
    return res


def _evaluate_bang(right: Object) -> Object:
    if type(right) == Integer:
        right = cast(Integer, right)
        return TRUE if (not right.value) else FALSE
    return TRUE if not _is_truthy(right) else FALSE


def _evaluate_identifier(node: ast.Identifier, env: Environment) -> Object:
    try:
        return env[node.value]
    except KeyError:
        return BUILTINS.get(node.value,
                            _new_error(_UNKNOWN_IDENT, [node.value]))


def _evaluate_positive(right: Object) -> Object:
    if type(right) != Integer:
        return _new_error(_UNKNOWN_PREFIX_OPER, ['+', right.type().name])
    right = cast(Integer, right)
    return Integer(+right.value)


def _evaluate_negative(right: Object) -> Object:
    if type(right) != Integer:
        return _new_error(_UNKNOWN_PREFIX_OPER, ['-', right.type().name])
    right = cast(Integer, right)
    return Integer(-right.value)


def _to_boolean_object(value: bool) -> Boolean:
    return TRUE if value else FALSE


def _is_truthy(obj: Object) -> bool:
    if (obj is NULL) or (obj is FALSE):
        return False
    else:
        return True


def _new_error(message: str, args: List[Any]) -> Error:
    return Error(message.format(*args))


def _evaluate_if_expr(if_expr: ast.If, env: Environment) -> Optional[Object]:
    assert if_expr.condition is not None
    cond = evaluate(if_expr.condition, env)
    assert cond is not None
    if _is_truthy(cond):
        assert if_expr.consequence is not None
        return evaluate(if_expr.consequence, env)
    elif if_expr.alternative is not None:
        return evaluate(if_expr.alternative, env)
    else:
        return NULL


def evaluate(node: ast.ASTNode, env: Environment) -> Optional[Object]:
    node_type: Type = type(node)
    if node_type == ast.Program:
        node = cast(ast.Program, node)
        return _evaluate_program(node, env)
    elif node_type == ast.ExpressionStatement:
        node = cast(ast.ExpressionStatement, node)
        assert node.expression is not None
        return evaluate(node.expression, env)
    elif node_type == ast.Expression:
        node = cast(ast.Expression, node)
        assert node is not None
    elif node_type == ast.Integer:
        node = cast(ast.Integer, node)
        assert node.value is not None
        return Integer(node.value)
    elif node_type == ast.Boolean:
        node = cast(ast.Boolean, node)
        assert node.value is not None
        return _to_boolean_object(node.value)
    elif node_type == ast.Prefix:
        node = cast(ast.Prefix, node)
        assert node.right is not None
        right = evaluate(node.right, env)
        assert right is not None
        return _evaluate_prefix_expr(node.operator, right)
    elif node_type == ast.Infix:
        node = cast(ast.Infix, node)
        assert node.left is not None and node.right is not None
        left = evaluate(node.left, env)
        right = evaluate(node.right, env)
        assert left is not None and right is not None
        return _evaluate_infix_expr(node.operator, left, right)
    elif node_type == ast.Block:
        node = cast(ast.Block, node)
        return _evaluate_block_statements(node, env)
    elif node_type == ast.If:
        node = cast(ast.If, node)
        return _evaluate_if_expr(node, env)
    elif node_type == ast.ReturnStatement:
        node = cast(ast.ReturnStatement, node)
        assert node.return_value is not None
        value = evaluate(node.return_value, env)
        assert value is not None
        return Return(value)
    elif node_type == ast.LetStatement:
        node = cast(ast.LetStatement, node)
        assert node.value is not None
        value = evaluate(node.value, env)
        assert value is not None and node.name is not None
        env[node.name.value] = value
        return value
    elif node_type == ast.Identifier:
        node = cast(ast.Identifier, node)
        return _evaluate_identifier(node, env)
    elif node_type == ast.Function:
        node = cast(ast.Function, node)
        assert node.body is not None
        func = Function(node.params,
                        node.body,
                        env)
        if node.name is not None:
            func.name = node.name
            env[node.name.value] = func
        return func
    # all line in var is register
    elif node_type == ast.Call:
        node = cast(ast.Call, node)
        assert node.func is not None
        function = evaluate(node.func, env)
        assert function is not None and node.args is not None
        args = _evaluate_expr(node.args, env)
        return _apply_func(function, args)
    elif node_type == ast.StringLiteral:
        node = cast(ast.StringLiteral, node)
        return String(node.value)
    return None
