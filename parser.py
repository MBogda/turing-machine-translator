from error import generate_error
from lexer import Token


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.token = lexer.next_token()

    def error_expected(self, expected):
        if not isinstance(expected, (tuple, list)):
            expected = (expected,)
        generate_error('Parser', 'expected {}, got {}'.format(
            ' or '.join(str(token) for token in expected), self.token.type
        ), self.token.line, self.token.column)
        # self.token = Token(Token.END_OF_FILE, '', 0, 0)

    def accept(self, token_types):
        if not isinstance(token_types, (tuple, tuple)):
            token_types = (token_types,)
        if self.token.type not in token_types:
            self.error_expected(token_types)
            while self.token.type not in token_types:
                self.token = self.lexer.next_token()
                if not self.token:
                    exit()
        self.token = self.lexer.next_token()

    def program(self):
        while self.token:
            self.instruction()

    def instruction(self):
        valid_tokens = (Token.IF, Token.WHILE, Token.OUTPUT_BOOLEAN, Token.OUTPUT_INTEGER, Token.OUTPUT_SYMBOL,
                        Token.OUTPUT_TAPE, Token.OUTPUT_ANY, Token.IDENTIFIER)
        if self.token.type not in valid_tokens:
            self.error_expected(valid_tokens)
            while self.token.type not in valid_tokens:
                self.token = self.lexer.next_token()
                if not self.token:
                    exit()

        if self.token.type == Token.IF:
            self.if_statement()
        elif self.token.type == Token.WHILE:
            self.while_statement()
        elif self.token.type in (Token.OUTPUT_BOOLEAN, Token.OUTPUT_INTEGER, Token.OUTPUT_SYMBOL,
                                 Token.OUTPUT_TAPE, Token.OUTPUT_ANY):
            self.output_statement()
        elif self.token.type == Token.IDENTIFIER:
            self.assignment()

    # todo? add one-line if, while
    def if_statement(self):
        self.accept(Token.IF)
        self.expression()
        self.accept(Token.COLON)
        self.accept(Token.NEWLINE)
        self.block_of_instructions()
        while self.token.type == Token.ELIF:
            self.accept(Token.ELIF)
            self.expression()
            self.accept(Token.COLON)
            self.accept(Token.NEWLINE)
            self.block_of_instructions()
        if self.token.type == Token.ELSE:
            self.accept(Token.ELSE)
            self.accept(Token.COLON)
            self.accept(Token.NEWLINE)
            self.block_of_instructions()

    def while_statement(self):
        self.accept(Token.WHILE)
        self.expression()
        self.accept(Token.COLON)
        self.accept(Token.NEWLINE)
        self.block_of_instructions()

    def block_of_instructions(self):
        self.accept(Token.INDENT)
        self.instruction()
        while self.token.type != Token.DEDENT:
            self.instruction()
        self.accept(Token.DEDENT)

    def output_statement(self):
        self.accept((Token.OUTPUT_BOOLEAN, Token.OUTPUT_INTEGER, Token.OUTPUT_SYMBOL,
                     Token.OUTPUT_TAPE, Token.OUTPUT_ANY))
        self.expression()
        self.accept(Token.NEWLINE)

    def assignment(self):
        self.accept(Token.IDENTIFIER)
        if self.token.type == Token.LEFT_SQUARE_BRACKET:
            self.accept(Token.LEFT_SQUARE_BRACKET)
            self.expression()
            self.accept(Token.RIGHT_SQUARE_BRACKET)
        elif self.token.type == Token.COLON:
            self.turing_machine_change_commands()
            return

        self.accept((Token.ASSIGNMENT, Token.ASSIGNMENT_PLUS, Token.ASSIGNMENT_MINUS, Token.ASSIGNMENT_MULTIPLY,
                     Token.ASSIGNMENT_DIVIDE, Token.ASSIGNMENT_MODULO))
        self.expression()
        if self.token.type == Token.COLON:
            self.turing_machine_change_commands()
        else:
            self.accept(Token.NEWLINE)

    def expression(self):
        self.subexpr1()
        while self.token.type == Token.OR:
            self.accept(Token.OR)
            self.subexpr1()

    def subexpr1(self):
        self.subexpr2()
        while self.token.type == Token.AND:
            self.accept(Token.AND)
            self.subexpr2()

    def subexpr2(self):
        while self.token.type == Token.NOT:
            self.accept(Token.NOT)

        self.subexpr3()
        if self.token.type in (Token.EQUAL, Token.NOT_EQUAL, Token.LESS, Token.GREATER,
                               Token.LESS_OR_EQUAL, Token.GREATER_OR_EQUAL):
            self.accept(self.token.type)
            self.subexpr3()

    def subexpr3(self):
        self.subexpr4()
        while self.token.type in (Token.PLUS, Token.MINUS):
            self.accept(self.token.type)
            self.subexpr4()

    def subexpr4(self):
        self.subexpr5()
        while self.token.type in (Token.MULTIPLY, Token.DIVIDE, Token.MODULO):
            self.accept(self.token.type)
            self.subexpr5()

    def subexpr5(self):
        self.term()
        while self.token.type in (Token.HEAD_PLUS, Token.HEAD_MINUS, Token.HEAD_MULTIPLY,
                                  Token.HEAD_DIVIDE, Token.HEAD_MODULO):
            self.accept(self.token.type)
            self.term()

    def term(self):
        valid_tokens = (Token.MINUS, Token.IDENTIFIER, Token.TRUE, Token.INTEGER_LITERAL, Token.SYMBOL_LITERAL,
                        Token.TAPE_LITERAL, Token.LEFT_BRACE, Token.INPUT_BOOLEAN, Token.INPUT_INTEGER,
                        Token.INPUT_SYMBOL, Token.INPUT_TAPE, Token.LEFT_BRACKET)
        if self.token.type not in valid_tokens:
            self.error_expected(valid_tokens)
            while self.token.type not in valid_tokens:
                self.token = self.lexer.next_token()
                if not self.token:
                    exit()

        while self.token.type == Token.MINUS:
            self.accept(Token.MINUS)

        # identifiers
        if self.token.type == Token.IDENTIFIER:
            self.accept(Token.IDENTIFIER)

        # literals
        elif self.token.type in (Token.TRUE, Token.FALSE, Token.INTEGER_LITERAL,
                                 Token.SYMBOL_LITERAL, Token.TAPE_LITERAL):
            self.accept(self.token.type)

        # turing machine literal
        elif self.token.type == Token.LEFT_BRACE:
            self.turing_machine_literal()

        # input statements
        elif self.token.type in (Token.INPUT_BOOLEAN, Token.INPUT_INTEGER, Token.INPUT_SYMBOL, Token.INPUT_TAPE):
            self.accept(self.token.type)

        # subexpression in parentheses
        elif self.token.type == Token.LEFT_BRACKET:
            self.accept(Token.LEFT_BRACKET)
            self.expression()
            self.accept(Token.RIGHT_BRACKET)

        # after handling term:
        if self.token.type == Token.LEFT_SQUARE_BRACKET:
            self.accept(Token.LEFT_SQUARE_BRACKET)
            if self.token.type != Token.RIGHT_SQUARE_BRACKET:
                self.expression()
            self.accept(Token.RIGHT_SQUARE_BRACKET)
        elif self.token.type == Token.LEFT_BRACKET:
            self.accept(Token.LEFT_BRACKET)
            self.expression()
            self.accept(Token.RIGHT_BRACKET)

    def turing_machine_literal(self):
        self.accept(Token.LEFT_BRACE)
        self.accept(Token.IDENTIFIER)
        self.accept(Token.SYMBOL_LITERAL)
        if self.token.type == Token.COLON:
            self.accept(Token.COLON)
            while self.token != Token.RIGHT_BRACE:
                self.turing_machine_command()
                self.accept(Token.COMMA)
        self.accept(Token.RIGHT_BRACE)

    def turing_machine_change_commands(self):
        self.accept(Token.COLON)
        self.accept(Token.NEWLINE)
        self.accept(Token.INDENT)
        while self.token.type != Token.DEDENT:
            self.turing_machine_command()
            self.accept(Token.NEWLINE)
        self.accept(Token.DEDENT)

    def turing_machine_command(self):
        self.accept(Token.IDENTIFIER)
        self.accept(Token.SYMBOL_LITERAL)
        self.accept(Token.ASSIGNMENT)
        self.accept((Token.IDENTIFIER, Token.MINUS))
        self.accept((Token.SYMBOL_LITERAL, Token.MINUS))
        self.accept((Token.LESS, Token.GREATER, Token.MINUS))

    def parse(self):
        self.program()
