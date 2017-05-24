import sys

from Lexer import Lexer

if __name__ == '__main__':
    program_file = sys.argv[1]
    with open(program_file) as file:
        program_text = file.read()

    lexer = Lexer(program_text)
    lexer.next_token()
    while lexer.token:
        print(lexer.token)
        lexer.next_token()
