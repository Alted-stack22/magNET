from abc import (
    ABC,
    abstractmethod
)
from typing import (
    cast,
    List,
    Optional
)
from src.token import Token


# Node types
class ASTNode(ABC):
    # Template, data structure node
    @abstractmethod
    # Returns the token literal
    def token_literal(self) -> str:
        pass

    @abstractmethod
    # Returns the string representation
    def __str__(self) -> str:
        pass


class Statement(ASTNode):
    # Token statement
    def __init__(self, token: Token) -> None:
        self.token = token

    # Token literal
    def token_literal(self) -> str:
        return self.token.literal


class Expression(ASTNode):
    # Token expression
    def __init__(self, token: Token) -> None:
        self.token = token

    # Token literal
    def token_literal(self) -> str:
        return self.token.literal


class Program(ASTNode):
    # Flow of statements and expressions
    def __init__(self, statements: List[Statement]) -> None:
        self.statements = statements

    def token_literal(self) -> str:
        # Returns the token literal for the statement
        if len(self.statements) > 0:
            return self.statements[0].token_literal()
        return ''

    def __str__(self) -> str:
        # Returns all statements in a string
        out: List[str] = []
        for statement in self.statements:
            out.append(str(statement))
        return ''.join(out)


class Identifier(Expression):
    # IDENT token and ASSIGNED value
    def __init__(self, token: Token, value: str) -> None:
        super().__init__(token)
        self.value = value

    def __str__(self) -> str:
        return self.value


class LetStatement(Statement):
    # Variable declaration
    def __init__(self,
                 token: Token,
                 name: Optional[Identifier] = None,
                 value: Optional[Expression] = None) -> None:
        super().__init__(token)
        self.name = name
        self.value = value

    def __str__(self) -> str:
        return f'{self.token_literal()} {str(self.name)} = {str(self.value)};'


class ReturnStatement(Statement):
    # Return statement
    def __init__(self,
                 token: Token,
                 return_value: Optional[Expression] = None) -> None:
        super().__init__(token)
        self.return_value = return_value

    def __str__(self) -> str:
        return f'{self.token_literal()} {str(self.return_value)}'


class ExpressionStatement(Statement):
    # Operations
    def __init__(self,
                 token: Token,
                 expression: Optional[Expression] = None) -> None:
        super().__init__(token)
        self.expression = expression

    def __str__(self) -> str:
        return str(self.expression)

    def format_expr(self) -> str:
        str_raw = str(self.expression)
        res = ''
        counter = 1
        for ind, char in enumerate(str_raw):
            if (len(str_raw) > (ind + 1)) and (str_raw[ind+1] == ')'):
                res += '\n'
                loops = 0
                while counter != loops:
                    res += '    '
                    loops += 1
                counter -= 1
            res += char
            if char == '(':
                res += '\n'
                loops = 0
                while counter != loops:
                    res += '    '
                    loops += 1
                counter += 1
        return res


class Integer(Expression):
    # Integer (a number)
    def __init__(self, token: Token, value: Optional[int] = None) -> None:
        super().__init__(token)
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class Boolean(Expression):
    # Boolean (true/false)
    def __init__(self, token: Token, value: Optional[bool] = None) -> None:
        super().__init__(token)
        self.value = value

    def __str__(self) -> str:
        return self.token_literal()


class StringLiteral(Expression):
    def __init__(self, token: Token, value: str) -> None:
        super().__init__(token)
        self.value = value

    def __str__(self) -> str:
        return self.token.literal


class Prefix(Expression):
    # Prefix operation (-1 or !True)
    def __init__(self, token: Token,
                 operator: str,
                 right: Optional[Expression] = None) -> None:
        super().__init__(token)
        self.operator = operator
        self.right = right

    def __str__(self) -> str:
        return f'({self.operator} {str(self.right)})'


class Infix(Expression):
    # Infix operation (1 + 2)
    def __init__(
            self,
            token: Token,
            left: Expression,
            operator: str,
            right: Optional[Expression] = None) -> None:
        super().__init__(token)
        self.left = left
        self.operator = operator
        self.right = right

    def __str__(self) -> str:
        return f'({str(self.left)} {self.operator} {str(self.right)})'


class Block(Statement):
    def __init__(self, token: Token, statements: List[Statement]) -> None:
        super().__init__(token)
        self.statements = statements

    def __str__(self) -> str:
        out: List[str] = [str(statement) for statement in self.statements]
        return ''.join(out)


class If(Expression):
    def __init__(self,
                 token: Token,
                 condition: Optional[Expression] = None,
                 consequence: Optional[Block] = None,
                 alternative: Optional[Block] = None) -> None:
        super().__init__(token)
        self.condition = condition
        self.consequence = consequence
        self.alternative = alternative

    def __str__(self) -> str:
        out: str = f'if {str(self.condition)} ' + '{' + \
                   f'{str(self.consequence)}' + '}'
        if self.alternative:
            out += f' else ' + '{' + f'{str(self.alternative)}' + '}'
        return out


class Function(Expression):
    def __init__(self,
                 token: Token,
                 params: List[Identifier] = [],
                 body: Optional[Block] = None,
                 name: Optional[Identifier] = None) -> None:
        super().__init__(token)
        self.params = params
        self.body = body
        self.name = name

    def __str__(self) -> str:
        params_list: List[str] = [str(param) for param in self.params]
        params: str = ', '.join(params_list)
        res: str = '{} '.format(self.token_literal())
        if self.name is not None:
            name = cast(Identifier, self.name)
            res += str(name) + ' '
        res += '({}) {{\n    {}\n}}'.format(params, str(self.body))
        return res


class Call(Expression):
    def __init__(self,
                 token: Token,
                 func: Expression,
                 args: Optional[List[Expression]] = None) -> None:
        super().__init__(token)
        self.func = func
        self.args = args

    def __str__(self) -> str:
        assert self.args is not None
        args_list: List[str] = [str(arg) for arg in self.args]
        args_str: str = ", ".join(args_list)
        return f'{self.func}({args_str})'
