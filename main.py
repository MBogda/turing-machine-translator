import sys

from error import init_program_text
from lexer import Lexer

if __name__ == '__main__':
    program_file = sys.argv[1]
    with open(program_file) as file:
        program_text = file.read()

    init_program_text(program_text)

    lexer = Lexer(program_text)
    lexer.next_token()
    while lexer.token:
        # print(lexer.token)
        lexer.next_token()
