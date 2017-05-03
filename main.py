import sys

from Lexer import Lexer

if __name__ == '__main__':
    program_file = sys.argv[1]
    with open(program_file) as file:
        program_text = file.read()

    lexer = Lexer(program_text)
    while True:
        lexer.next_token()
        print(lexer.tokens[lexer.category], lexer.value)
        if lexer.category == Lexer.EOF:
            break

# todo: добавить инденты и комменты
# todo: добавить символы и строки
