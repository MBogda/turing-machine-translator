import sys

from error import init_program_text
from lexer import Lexer
from parser import Parser


def main():
    try:
        program_file = sys.argv[1]
    except IndexError:
        print('Need to specify file program name to compile')
        return
    try:
        with open(program_file, 'r') as file:
            program_text = file.read()
    except FileNotFoundError:
        print("No such file: '{}'".format(program_file))
        return

    init_program_text(program_text)

    # lexer = Lexer(program_text)
    # token = lexer.next_token()
    # while token:
    #     # print(token)
    #     token = lexer.next_token()
    parser = Parser(Lexer(program_text))
    parser.parse()

if __name__ == '__main__':
    main()
