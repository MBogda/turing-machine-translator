from Lexer import Lexer

if __name__ == '__main__':
    lexer = Lexer('123 kuku privet !№# \nvasya = {kuku \\\'au\' \n\n\n!<@}: <b >><<><!= \\\n kuku \\')
    lexer.next_token()
    while lexer.category != lexer.EOF:
        print(lexer.tokens[lexer.category], lexer.value)
        lexer.next_token()

# todo: добавить инденты и комменты
# todo: добавить символы и строки
