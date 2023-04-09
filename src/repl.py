import readline
from os import (
    name,
    system
)
from typing import List
from src.object import (
    Environment,
    ObjectType
)
from src.evaluator import evaluate
from src.ast import Program
from src.parser import Parser
from src.lexer import Lexer
from src.token import (
    Token,
    TokenType
)


# End of command
EOF_TOKEN: Token = Token(TokenType.EOF, '')


def _show_errors(errors: List[str]) -> None:
    for error in errors:
        print(error)


def _clean_console() -> None:
    # For windows
    if name == 'nt':
        _ = system("cls")
    # For macOS/Linux
    else:  # return posix
        _ = system("clear")


def start_repl() -> None:
    # Interactive mode
    scanned: List[str] = []
    while (source := input('>> ')) != 'exit()':
        if source == 'clean()':
            _clean_console()
            continue
        elif source == 'show()':
            print(scanned)
            continue
        scanned.append(source)
        lexer: Lexer = Lexer(' '.join(scanned))
        parser: Parser = Parser(lexer)
        program: Program = parser.parse_program()
        env: Environment = Environment()
        if len(parser.errors) > 0:
            _show_errors(parser.errors)
            scanned.remove(source)
            continue
        evaluated = evaluate(program, env)
        # print('Eval:', evaluated)  # Object
        if evaluated is not None:
            print('Inspect:', evaluated.inspect())  # Readable
            # print('Type:', evaluated.type())  # Type
            if evaluated.type() == ObjectType.ERROR:
                scanned.remove(source)
        else: print("Not implemented yet!")
