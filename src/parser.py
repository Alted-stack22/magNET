from enum import IntEnum
from typing import (
    Callable,
    Dict,
    List,
    Optional
)
from src.ast import (
    Block,
    Boolean,
    Call,
    Expression,
    ExpressionStatement,
    Function,
    Identifier,
    If,
    Infix,
    Integer,
    LetStatement,
    Prefix,
    Program,
    ReturnStatement,
    Statement,
    StringLiteral
)
from src.lexer import Lexer
from src.token import (
    Token,
    TokenType
)


# def (self) -> Optional[Expression]
PrefixParseFn = Callable[[], Optional[Expression]]
# def (self, Expression) -> Optional[Expression]
InfixParseFn = Callable[[Expression], Optional[Expression]]

PrefixParseFns = Dict[TokenType, PrefixParseFn]
InfixParseFns = Dict[TokenType, InfixParseFn]


class Precedence(IntEnum):
    LOWEST = 1
    EQUALS = 2
    LESSGREATER = 3
    SUM = 4
    PRODUCT = 5
    PREFIX = 6
    CALL = 7


PRECEDENCES: Dict[TokenType, Precedence] = {
    TokenType.EQUALS: Precedence.EQUALS,
    TokenType.NOT_EQUALS: Precedence.EQUALS,
    TokenType.LT: Precedence.LESSGREATER,
    TokenType.GT: Precedence.LESSGREATER,
    TokenType.LE: Precedence.LESSGREATER,
    TokenType.GE: Precedence.LESSGREATER,
    TokenType.PLUS: Precedence.SUM,
    TokenType.MINUS: Precedence.SUM,
    TokenType.MULTIPLICATION: Precedence.PRODUCT,
    TokenType.DIVISION: Precedence.PRODUCT,
    TokenType.NEGATION: Precedence.PREFIX,
    TokenType.AND: Precedence.LESSGREATER,
    TokenType.OR: Precedence.LESSGREATER,
    TokenType.XOR: Precedence.LESSGREATER,
    TokenType.LPAREN: Precedence.CALL
}


# Top-Down
# Bottom-Up
#* Pratt Parser
#! Parse tokens with (unique) parsing functions
class Parser:
    # Check syntax and generate an AST
    def __init__(self, lexer: Lexer) -> None:
        self._lexer = lexer
        self._current_token: Optional[Token] = None
        self._peek_token: Optional[Token] = None
        self._errors: List[str] = []
        # Register prefixes and infixes
        self._prefix_parse_fns: PrefixParseFns = self._register_prefix_fns()
        self._infix_parse_fns: InfixParseFns = self._register_infix_fns()
        # Set cursor position
        self._advance_tokens()
        self._advance_tokens()

    @property
    def errors(self) -> List[str]:
        # Parser generated error messages
        return self._errors

    def parse_program(self) -> Program:
        # Generate statements items
        program: Program = Program(statements=[])
        assert self._current_token is not None
        while self._current_token.token_type != TokenType.EOF:
            statement = self._parse_statement()
            if statement is not None:
                program.statements.append(statement)
            self._advance_tokens()
        return program

    def _advance_tokens(self) -> None:
        # Select current and next_token
        self._current_token = self._peek_token
        self._peek_token = self._lexer.next_token()

    def _expected_token(self, token_type: TokenType) -> bool:
        assert self._peek_token is not None
        # Check the token type of the following token (SYNTAX)
        if self._peek_token.token_type == token_type:
            self._advance_tokens()
            return True
        self._expected_token_error(token_type)
        return False

    def _expected_token_error(self, token_type: TokenType) -> None:
        assert self._peek_token is not None
        # Syntax error
        error_msg = f"Expected token: {token_type}" + \
            f" but the token inserted is: {self._peek_token}"
        self._errors.append(error_msg)

    def _parse_let_statement(self) -> Optional[LetStatement]:
        # Assign token
        assert self._current_token is not None
        let_statement = LetStatement(token=self._current_token)
        # Assign ident
        if not self._expected_token(TokenType.IDENT):
            return None
        # * let_statement.name = Identifier(token=self._current_token,
        # *                                 value=self._current_token.literal)
        let_statement.name = self._parse_identifier()
        # Assign expression
        if not self._expected_token(TokenType.ASSIGN):
            return None
        self._advance_tokens()
        let_statement.value = self._parse_expression(Precedence.LOWEST)
        assert self._peek_token is not None
        if self._peek_token.token_type == TokenType.SEMICOLON:
            self._advance_tokens()
        return let_statement

    def _parse_return_statement(self) -> Optional[ReturnStatement]:
        # Assign token
        assert self._current_token is not None
        return_statement = ReturnStatement(token=self._current_token)
        self._advance_tokens()
        return_statement.return_value = self._parse_expression(
            Precedence.LOWEST)
        assert self._peek_token is not None
        if self._peek_token.token_type == TokenType.SEMICOLON:
            self._advance_tokens()
        return return_statement

    def _parse_expression_statement(self) -> Optional[ExpressionStatement]:
        assert self._current_token is not None
        # Create expression statement
        expression_statement = ExpressionStatement(token=self._current_token)
        expression_statement.expression = self._parse_expression(
            Precedence.LOWEST)
        assert self._peek_token is not None
        if self._peek_token.token_type == TokenType.SEMICOLON:
            self._advance_tokens()
        return expression_statement

    def _peek_precedence(self) -> Precedence:
        assert self._peek_token is not None
        # Next token precedence
        try:
            return PRECEDENCES[self._peek_token.token_type]
        except KeyError:
            return Precedence.LOWEST

    def _parse_call_args(self) -> Optional[List[Expression]]:
        expr_list: List[Expression] = []
        assert self._peek_token is not None
        if self._peek_token.token_type == TokenType.RPAREN:
            self._advance_tokens()
            return expr_list
        self._advance_tokens()

        # if expr := self._parse_expression(Precedence.LOWEST):
        #     expr_list.append(expr)
        # while self._peek_token.token_type == TokenType.COMMA:
        #     self._advance_tokens()
        #     self._advance_tokens()
        #     if expr := self._parse_expression(Precedence.LOWEST):
        #         expr_list.append(expr)

        # As do-while
        while True:
            if expr := self._parse_expression(Precedence.LOWEST):
                expr_list.append(expr)
            if self._peek_token.token_type == TokenType.COMMA:
                self._advance_tokens()
                self._advance_tokens()
            else:
                break
        if not self._expected_token(TokenType.RPAREN):
            return None
        return expr_list

    def _parse_call(self, func: Expression) -> Call:
        assert self._current_token is not None
        call = Call(self._current_token, func)
        call.args = self._parse_call_args()
        return call

    def _parse_expression(
            self,
            precedence: Precedence) -> Optional[Expression]:
        # Parse an expression
        assert self._current_token is not None
        # Parse based on token (prefix)
        try:
            prefix_parse_fn = self._prefix_parse_fns[self._current_token.token_type]
        except KeyError:
            message = f'No function found to parse: {self._current_token.literal}'
            self._errors.append(message)
            return None
        left_expression = prefix_parse_fn()
        assert self._peek_token is not None
        # Parse based on token (suffix)
        while not self._peek_token.token_type == TokenType.SEMICOLON and precedence < self._peek_precedence():
            try:
                infix_parse_fn = self._infix_parse_fns[self._peek_token.token_type]
                self._advance_tokens()
                assert left_expression is not None
                left_expression = infix_parse_fn(left_expression)
            except BaseException:
                return left_expression
        return left_expression

    def _parse_statement(self) -> Optional[Statement]:
        assert self._current_token is not None
        # Check type statement
        if self._current_token.token_type == TokenType.LET or \
                self._current_token.token_type == TokenType.VAR or \
                self._current_token.token_type == TokenType.CONST:
            return self._parse_let_statement()
        elif self._current_token.token_type == TokenType.RETURN:
            return self._parse_return_statement()
        else:
            return self._parse_expression_statement()

    def _parse_string_literal(self) -> Expression:
        assert self._current_token is not None
        return StringLiteral(token=self._current_token,
                             value=self._current_token.literal)

    def _parse_integer(self) -> Optional[Integer]:
        assert self._current_token is not None
        # Create integer
        integer = Integer(token=self._current_token)
        try:
            integer.value = int(self._current_token.literal)
        except ValueError:
            message = f'Is not an integer: {self._current_token}'
            self._errors.append(message)
            return None
        return integer

    def _parse_identifier(self) -> Identifier:
        assert self._current_token is not None
        # Create identifier
        return Identifier(
            token=self._current_token,
            value=self._current_token.literal)

    def _parse_boolean(self) -> Boolean:
        assert self._current_token is not None
        # Create boolean
        return Boolean(token=self._current_token,
                       value=self._current_token.token_type == TokenType.TRUE)

    def _parse_block(self) -> Block:
        assert self._current_token is not None
        block_statement = Block(token=self._current_token,
                                statements=[])
        self._advance_tokens()
        while not self._current_token.token_type == TokenType.RBRACE \
                and not self._current_token.token_type == TokenType.EOF:
            statement = self._parse_statement()
            if statement:
                block_statement.statements.append(statement)
            self._advance_tokens()
        return block_statement

    def _parse_grouped_expression(self) -> Optional[Expression]:
        self._advance_tokens()
        expression = self._parse_expression(Precedence.LOWEST)
        if not self._expected_token(TokenType.RPAREN):
            return None
        return expression

    def _parse_if(self) -> Optional[If]:
        assert self._current_token is not None
        if_expression = If(token=self._current_token)
        if not self._expected_token(TokenType.LPAREN):
            return None
        self._advance_tokens()
        if_expression.condition = self._parse_expression(Precedence.LOWEST)
        if not self._expected_token(TokenType.RPAREN):
            return None
        if not self._expected_token(TokenType.LBRACE):
            return None
        if_expression.consequence = self._parse_block()
        assert self._peek_token is not None
        if self._peek_token.token_type == TokenType.ELSE:
            self._advance_tokens()
            if not self._expected_token(TokenType.LBRACE):
                return None
            if_expression.alternative = self._parse_block()
        return if_expression

    #* My progress
    def _parse_func_params(self) -> List[Identifier]:
        params: List[Identifier] = []
        assert self._peek_token is not None
        if self._peek_token.token_type == TokenType.RPAREN:
            self._advance_tokens()
            return params
        self._advance_tokens()
        assert self._current_token is not None
        params.append(self._parse_identifier())
        assert self._peek_token is not None
        while self._peek_token.token_type == TokenType.COMMA and \
                  self._peek_token.token_type != TokenType.EOF:
            self._advance_tokens()
            self._advance_tokens()
            params.append(self._parse_identifier())
        if not self._expected_token(TokenType.RPAREN):
            return []
        return params

    # * My progress
    def _parse_function(self) -> Optional[Function]:
        assert self._current_token is not None
        function = Function(token=self._current_token)
        assert self._peek_token is not None
        if self._peek_token.token_type == TokenType.IDENT:
            self._advance_tokens()
            function.name = self._parse_identifier()
        if not self._expected_token(TokenType.LPAREN):
            return None
        #* With unique parse function
        function.params = self._parse_func_params()
        #! Infinite loop
        # assert self._peek_token is not None
        # while self._peek_token.token_type != TokenType.RPAREN and \
        #         self._peek_token.token_type != TokenType.EOF:
        #     self._advance_tokens()
        #     assert self._current_token is not None
        #     if self._current_token.token_type == TokenType.COMMA:
        #         continue
        #     function.params.append(self._parse_identifier())
        # self._advance_tokens()
        #! Overwrite attribute
        assert self._peek_token is not None
        if not self._expected_token(TokenType.LBRACE):
            return None
        function.body = self._parse_block()
        return function


    def _register_prefix_fns(self) -> PrefixParseFns:
        # Prefix registry
        return {
            TokenType.TRUE: self._parse_boolean,
            TokenType.FALSE: self._parse_boolean,
            TokenType.IDENT: self._parse_identifier,
            TokenType.INT: self._parse_integer,
            TokenType.MINUS: self._parse_prefix_expression,
            TokenType.NEGATION: self._parse_prefix_expression,
            TokenType.LPAREN: self._parse_grouped_expression,
            TokenType.IF: self._parse_if,
            TokenType.ELSE: self._parse_if,
            TokenType.FUNCTION: self._parse_function,
            TokenType.STRING: self._parse_string_literal
        }

    def _register_infix_fns(self) -> InfixParseFns:
        # Suffix registry
        return {
            TokenType.ASSIGN: self._parse_infix_expression,
            TokenType.PLUS: self._parse_infix_expression,
            TokenType.MINUS: self._parse_infix_expression,
            TokenType.MULTIPLICATION: self._parse_infix_expression,
            TokenType.DIVISION: self._parse_infix_expression,
            TokenType.EQUALS: self._parse_infix_expression,
            TokenType.NOT_EQUALS: self._parse_infix_expression,
            TokenType.LT: self._parse_infix_expression,
            TokenType.GT: self._parse_infix_expression,
            TokenType.LE: self._parse_infix_expression,
            TokenType.GE: self._parse_infix_expression,
            TokenType.AND: self._parse_infix_expression,
            TokenType.OR: self._parse_infix_expression,
            TokenType.XOR: self._parse_infix_expression,
            TokenType.LPAREN: self._parse_call
        }

    def _current_precedence(self) -> Precedence:
        assert self._current_token is not None
        # Current token precedence
        try:
            return PRECEDENCES[self._current_token.token_type]
        except KeyError:
            return Precedence.LOWEST

    def _parse_prefix_expression(self) -> Prefix:
        assert self._current_token is not None
        # Create prefix
        prefix_expression = Prefix(token=self._current_token,
                                   operator=self._current_token.literal)
        self._advance_tokens()
        prefix_expression.right = self._parse_expression(Precedence.PREFIX)
        return prefix_expression

    def _parse_infix_expression(self, left: Expression) -> Infix:
        assert left is not None
        # Create infix
        assert self._current_token is not None
        infix_expression = Infix(token=self._current_token,
                                 left=left,
                                 operator=self._current_token.literal)
        precedence = self._current_precedence()
        self._advance_tokens()
        infix_expression.right = self._parse_expression(precedence)
        return infix_expression
