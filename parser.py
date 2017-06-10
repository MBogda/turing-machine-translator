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
        while self.token:
            self.instruction()

    def instruction(self):
        if self.token.type == 'IF':
            self.if_()
        elif self.token.type == 'WHILE':
            self.while_()
        elif self.token.type in ['OUTPUT_BOOLEAN', 'OUTPUT_INTEGER', 'OUTPUT_SYMBOL', 'OUTPUT_TAPE', 'OUTPUT_ANY']:
            self.output()
        elif self.token.type == 'IDENTIFIER':
            self.assignment()
        else:
            generate_error(
                'Parser',
                'expected IF or WHILE or OUTPUT or IDENTIFIER, got {}'.format(
                    self.token.type),
                self.token.line, self.token.column)

    def if_(self):
        self.accept('IF')
        self.boolean_expression()
        self.accept('COLON')
        self.accept('NEWLINE')  # todo? add one-line if
        self.block_of_instructions()

    def while_(self):
        self.accept('WHILE')
        self.boolean_expression()
        self.accept('COLON')
        self.accept('NEWLINE')
        self.block_of_instructions()

    def block_of_instructions(self): pass

    def output(self):
        if self.token.type == 'OUTPUT_BOOLEAN':
            self.accept('OUTPUT_BOOLEAN')
            self.boolean_expression()
        elif self.token.type == 'OUTPUT_INTEGER':
            self.accept('OUTPUT_INTEGER')
            self.integer_expression()
        elif self.token.type == 'OUTPUT_SYMBOL':
            self.accept('OUTPUT_SYMBOL')
            self.symbol_expression()
        elif self.token.type == 'OUTPUT_TAPE':
            self.accept('OUTPUT_TAPE')
            self.tape_expression()
        elif self.token.type == 'OUTPUT_ANY':   # ???
            self.accept('OUTPUT_ANY')
            self.any_expression()

    def assignment(self):
        self.accept('IDENTIFIER')
        if self.token.type == 'LEFT_SQUARE_BRACKET':
            self.accept('LEFT_SQUARE_BRACKET')
            self.integer_expression()
            self.accept('RIGHT_SQUARE_BRACKET')
        self.accept('ASSIGNMENT')
        # todo ...

    def boolean_expression(self): pass

    def integer_expression(self):
        self.integer_term()
        while self.token.type in ['PLUS', 'MINUS']:
            self.accept(self.token.type)
            self.integer_term()

    def integer_term(self):
        self.integer_multiplier()
        while self.token.type in ['MULTIPLY', 'DIVIDE', 'MODULO']:
            self.accept(self.token.type)
            self.integer_multiplier()

    def integer_multiplier(self):
        if self.token.type == 'MINUS':
            self.accept('MINUS')

        if self.token.type == 'IDENTIFIER':
            self.accept('IDENTIFIER')
        elif self.token.type == 'INTEGER_LITERAL':
            self.accept('INTEGER_LITERAL')
        elif self.token.type == 'INPUT_INTEGER':
            self.accept('INPUT_INTEGER')
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

    def symbol_expression(self): pass

    def tape_expression(self): pass

    def any_expression(self): pass

    def parse(self):
        self.integer_expression()
        if self.token.type == 'NEWLINE':
            print('OK')
        else:
            generate_error('Parser', self.token, self.token.line, self.token.column)
