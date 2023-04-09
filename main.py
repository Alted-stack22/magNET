from datetime import datetime
from src.repl import start_repl


def run() -> None:
    now = datetime.now()
    print('magNET 1.0 (main, {}/{}/{})'.format(now.month, now.day, now.year))
    print('Type "clean", "show" for more options.')
    start_repl()


if __name__ == '__main__':
    run()
