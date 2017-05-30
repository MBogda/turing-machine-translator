from error import generate_error


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.token = lexer.next_token()

    def accept(self, token_type):
        if self.token.type == token_type:
            self.token = self.lexer.next_token()
        else:
            generate_error('Parser', 'expected token {}, got {}'.format(token_type, self.token.type),
                           self.token.line, self.token.column)

    def program(self):
        self.instruction()
        if self.token:
            self.program()

    def instruction(self):
        if self.token.type == 'KEYWORD' and self.token.value == 'if':
            pass
        # elif ...

    def integer_expression(self):
        self.integer_term()
        while self.token.type == 'ARITHMETIC_OPERATOR' and self.token.value in ['+', '-']:
            self.accept('ARITHMETIC_OPERATOR')
            self.integer_term()

    def integer_term(self):
        self.integer_multiplier()
        while self.token.type == 'ARITHMETIC_OPERATOR' and self.token.value in ['*', '/', '%']:
            self.accept('ARITHMETIC_OPERATOR')
            self.integer_multiplier()

    def integer_multiplier(self):
        if self.token.type == 'ARITHMETIC_OPERATOR' and self.token.value == '-':
            self.accept('ARITHMETIC_OPERATOR')

        if self.token.type == 'IDENTIFIER':
            self.accept('IDENTIFIER')
        elif self.token.type == 'INTEGER_LITERAL':
            self.accept('INTEGER_LITERAL')
        elif self.token.type == 'INPUT_OPERATOR' and self.token.value == '>i':
            self.accept('INPUT_OPERATOR')
        elif self.token.type == 'LEFT_BRACKET':
            self.accept('LEFT_BRACKET')
            self.integer_expression()
            self.accept('RIGHT_BRACKET')
        else:
            generate_error(
                'Parser',
                'expected IDENTIFIER or INTEGER_LITERAL or INPUT_OPERATOR or LEFT_BRACKET, got {}'.format(
                    self.token.type),
                self.token.line, self.token.column)

    def parse(self):
        self.integer_expression()
        if self.token.type == 'NEWLINE':
            print('OK')
        else:
            generate_error('Parser', self.token, self.token.line, self.token.column)
