from lexical_analysis import Lexer

if __name__ == '__main__':
    lexer = Lexer('123 kuku privet !№# \nvasya = {kuku \\\'au\'}:')
    lexer.next_token()
    while lexer.category != lexer.EOF:
        print(lexer.tokens[lexer.category], lexer.value)
        lexer.next_token()

# добавить инденты и комменты
# добавить символы и строки
# добавить переход на новую строку
# не захватывать жадно одинарные специальные символы
