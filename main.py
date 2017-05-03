from lexical_analysis import Lexer

if __name__ == '__main__':
    lexer = Lexer('123 kuku privet !№# \nvasya = {kuku \\\'au\' !<@}: <b >><<><!=')
    lexer.next_token()
    while lexer.category != lexer.EOF:
        print(lexer.tokens[lexer.category], lexer.value)
        lexer.next_token()

# todo: добавить инденты и комменты
# todo: добавить символы и строки
# todo: добавить объединение строк кода по обратному слэшу
# todo: добавить переход на новую строку

# done:
# не захватывать жадно одинарные специальные символы
