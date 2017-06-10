from error import generate_error
from lexer import Token


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
        if self.token.type == Token.IF:
            self.if_()
        elif self.token.type == Token.WHILE:
            self.while_()
        elif self.token.type in [Token.OUTPUT_BOOLEAN, Token.OUTPUT_INTEGER, Token.OUTPUT_SYMBOL,
                                 Token.OUTPUT_TAPE, Token.OUTPUT_ANY]:
            self.output()
        elif self.token.type == Token.IDENTIFIER:
            self.assignment()
        else:
            generate_error(
                'Parser',
                'expected IF or WHILE or OUTPUT or IDENTIFIER, got {}'.format(
                    self.token.type),
                self.token.line, self.token.column)

    # todo? add one-line if, while
    def if_(self):
        self.accept(Token.IF)
        self.boolean_expression()
        self.accept(Token.COLON)
        self.accept(Token.NEWLINE)
        self.block_of_instructions()
        while self.token.type == Token.ELIF:
            self.accept(Token.ELIF)
            self.boolean_expression()
            self.accept(Token.COLON)
            self.accept(Token.NEWLINE)
            self.block_of_instructions()
        if self.token.type == Token.ELSE:
            self.accept(Token.ELSE)
            self.accept(Token.COLON)
            self.accept(Token.NEWLINE)
            self.block_of_instructions()

    def while_(self):
        self.accept(Token.WHILE)
        self.boolean_expression()
        self.accept(Token.COLON)
        self.accept(Token.NEWLINE)
        self.block_of_instructions()

    def block_of_instructions(self):
        self.accept(Token.INDENT)
        self.instruction()
        while self.token.type != Token.DEDENT:
            self.instruction()
        self.accept(Token.DEDENT)

    def output(self):
        if self.token.type == Token.OUTPUT_BOOLEAN:
            self.accept(Token.OUTPUT_BOOLEAN)
            self.boolean_expression()
        elif self.token.type == Token.OUTPUT_INTEGER:
            self.accept(Token.OUTPUT_INTEGER)
            self.integer_expression()
        elif self.token.type == Token.OUTPUT_SYMBOL:
            self.accept(Token.OUTPUT_SYMBOL)
            self.symbol_expression()
        elif self.token.type == Token.OUTPUT_TAPE:
            self.accept(Token.OUTPUT_TAPE)
            self.tape_expression()
        elif self.token.type == Token.OUTPUT_ANY:  # ???
            self.accept(Token.OUTPUT_ANY)
            self.any_expression()

    def assignment(self):
        self.accept(Token.IDENTIFIER)
        if self.token.type == Token.LEFT_SQUARE_BRACKET:
            self.accept(Token.LEFT_SQUARE_BRACKET)
            self.integer_expression()
            self.accept(Token.RIGHT_SQUARE_BRACKET)
        self.accept(Token.ASSIGNMENT)
        # todo ...

    def boolean_expression(self):
        self.boolean_term()
        while self.token.type == Token.OR:
            self.accept(Token.OR)
            self.boolean_term()

    def boolean_term(self):
        self.boolean_multiplier()
        while self.token.type == Token.AND:
            self.accept(Token.AND)
            self.boolean_multiplier()

    def boolean_multiplier(self):
        self.integer_expression()
        while self.token.type in [Token.EQUAL, Token.NOT_EQUAL, Token.LESS, Token.GREATER,
                                  Token.LESS_OR_EQUAL, Token.GREATER_OR_EQUAL]:
            self.accept(self.token.type)
            self.integer_expression()

    def integer_expression(self):
        self.integer_term()
        while self.token.type in [Token.PLUS, Token.MINUS]:
            self.accept(self.token.type)
            self.integer_term()

    def integer_term(self):
        self.integer_multiplier()
        while self.token.type in [Token.MULTIPLY, Token.DIVIDE, Token.MODULO]:
            self.accept(self.token.type)
            self.integer_multiplier()

    def integer_multiplier(self):
        if self.token.type == Token.MINUS:
            self.accept(Token.MINUS)

        if self.token.type == Token.IDENTIFIER:
            self.accept(Token.IDENTIFIER)
            if self.token.type == Token.LEFT_SQUARE_BRACKET:
                self.accept(Token.LEFT_SQUARE_BRACKET)
                self.accept(Token.RIGHT_SQUARE_BRACKET)
        elif self.token.type == Token.INTEGER_LITERAL:
            self.accept(Token.INTEGER_LITERAL)
        elif self.token.type == Token.INPUT_INTEGER:
            self.accept(Token.INPUT_INTEGER)
        elif self.token.type == Token.LEFT_BRACKET:
            self.accept(Token.LEFT_BRACKET)
            # self.integer_expression()
            self.boolean_expression()
            self.accept(Token.RIGHT_BRACKET)
        else:
            generate_error(
                'Parser',
                'expected IDENTIFIER or INTEGER_LITERAL or INPUT_OPERATOR or LEFT_BRACKET, got {}'.format(
                    self.token.type),
                self.token.line, self.token.column)

    def symbol_expression(self):
        pass

    def tape_expression(self):
        pass

    def any_expression(self):
        pass

    def parse(self):
        self.integer_expression()
        if self.token.type == Token.NEWLINE:
            print('OK')
        else:
            generate_error('Parser', self.token, self.token.line, self.token.column)
