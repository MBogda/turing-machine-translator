from source import ast
from source.ast import Type
from source.error import generate_error
from source.lexer import Lexer, Token


class Parser:
    def __init__(self, program_text: str):
        self.lexer = Lexer(program_text)
        self.token = self.lexer.next_token()

    def parse(self):
        return self.program()

    def error_expected_token_type(self, token_types):
        if not isinstance(token_types, (tuple, list)):
            token_types = (token_types,)
        generate_error('Parser', 'expected token {}, got {}'.format(
            ' or '.join(str(token) for token in token_types), self.token.type
        ), self.token.line, self.token.column)

    def accept(self, token_types) -> Token:
        if not isinstance(token_types, (tuple, tuple)):
            token_types = (token_types,)
        if self.token.type not in token_types:
            self.error_expected_token_type(token_types)
            # wait for valid token
            while self.token.type not in token_types:
                self.token = self.lexer.next_token()
                if not self.token:
                    assert False, 'End of program text'
        accepted_token = self.token
        self.token = self.lexer.next_token()
        return accepted_token

    def program(self):
        program = ast.InstructionSequence()
        while self.token:
            program.instructions.append(self.instruction())
        return program

    def instruction(self):
        # wait for valid token
        valid_tokens = (Token.IF, Token.WHILE, Token.OUTPUT_BOOLEAN, Token.OUTPUT_INTEGER, Token.OUTPUT_SYMBOL,
                        Token.OUTPUT_TAPE, Token.OUTPUT_ANY, Token.IDENTIFIER)
        if self.token.type not in valid_tokens:
            self.error_expected_token_type(valid_tokens)
            while self.token.type not in valid_tokens:
                self.token = self.lexer.next_token()
                if not self.token:
                    assert False, 'End of program text'

        if self.token.type == Token.IF:
            return self.if_statement()
        elif self.token.type == Token.WHILE:
            return self.while_statement()
        elif self.token.type in (Token.OUTPUT_BOOLEAN, Token.OUTPUT_INTEGER, Token.OUTPUT_SYMBOL,
                                 Token.OUTPUT_TAPE, Token.OUTPUT_ANY):
            return self.output_statement()
        elif self.token.type == Token.IDENTIFIER:
            return self.assignment_statement()

    # todo? add one-line if, while
    def if_statement(self):
        statement = ast.IfStatement()
        self.accept(Token.IF)
        statement.condition = self.expression()
        self.accept(Token.COLON)
        self.accept(Token.NEWLINE)
        statement.if_body = self.block_of_instructions()
        last_if = statement
        while self.token.type == Token.ELIF:
            elif_statement = ast.IfStatement()
            self.accept(Token.ELIF)
            # statement.elif_condition.append(self.expression())
            elif_statement.condition = self.expression()
            self.accept(Token.COLON)
            self.accept(Token.NEWLINE)
            # statement.elif_body.append(self.block_of_instructions())
            elif_statement.if_body = self.block_of_instructions()
            last_if.else_body = elif_statement
            last_if = elif_statement
        if self.token.type == Token.ELSE:
            self.accept(Token.ELSE)
            self.accept(Token.COLON)
            self.accept(Token.NEWLINE)
            last_if.else_body = self.block_of_instructions()
        return statement

    def while_statement(self):
        statement = ast.WhileStatement()
        self.accept(Token.WHILE)
        statement.condition = self.expression()
        self.accept(Token.COLON)
        self.accept(Token.NEWLINE)
        statement.body = self.block_of_instructions()

    def block_of_instructions(self):
        sequence = ast.InstructionSequence()
        self.accept(Token.INDENT)
        sequence.instructions.append(self.instruction())
        while self.token.type != Token.DEDENT:
            sequence.instructions.append(self.instruction())
        self.accept(Token.DEDENT)
        return sequence

    def output_statement(self):
        statement = ast.OutputStatement()
        accepted = self.accept((Token.OUTPUT_BOOLEAN, Token.OUTPUT_INTEGER, Token.OUTPUT_SYMBOL,
                                Token.OUTPUT_TAPE, Token.OUTPUT_ANY))
        statement.token = accepted
        if accepted.type == Token.OUTPUT_BOOLEAN:
            statement.type = Type.BOOLEAN
        if accepted.type == Token.OUTPUT_INTEGER:
            statement.type = Type.INTEGER
        if accepted.type == Token.OUTPUT_SYMBOL:
            statement.type = Type.SYMBOL
        if accepted.type == Token.OUTPUT_TAPE:
            statement.type = Type.TAPE
        # OUTPUT_ANY is coded as None
        statement.value = self.expression()
        self.accept(Token.NEWLINE)
        return statement

    def assignment_statement(self):
        statement = ast.AssignmentStatement()
        left = ast.Identifier()
        accepted = self.accept(Token.IDENTIFIER)
        left.token = accepted
        left.name = accepted.value

        # handle identifier[expression]
        if self.token.type == Token.LEFT_SQUARE_BRACKET:
            left_left = left
            left = ast.Expression()
            left.left = left_left
            accepted = self.accept(Token.LEFT_SQUARE_BRACKET)
            left.token = accepted
            left.operator = accepted.type
            left.right = self.expression()
            self.accept(Token.RIGHT_SQUARE_BRACKET)

        # handle identifier^
        elif self.token.type == Token.HEAD:
            left_left = left
            left = ast.Expression()
            accepted = self.accept(Token.HEAD)
            left.token = accepted
            left.left = left_left
            left.unary_operator = accepted.type

        # handle identifier: \n <turing machine instruction sequence>
        elif self.token.type == Token.COLON:
            statement.token = self.token
            statement.left = left
            statement.operator = self.token.type
            statement.right = self.turing_machine_instruction_sequence()
            return statement

        statement.left = left
        accepted = self.accept((Token.ASSIGNMENT, Token.ASSIGNMENT_PLUS, Token.ASSIGNMENT_MINUS,
                                Token.ASSIGNMENT_MULTIPLY, Token.ASSIGNMENT_DIVIDE, Token.ASSIGNMENT_MODULO))
        statement.token = accepted
        statement.operator = accepted.type
        statement.right = self.expression()
        self.accept(Token.NEWLINE)
        return statement

    def expression(self, level=0):
        operators = [
            (Token.OR,),
            (Token.AND,),
            (Token.NOT,),
            (Token.EQUAL, Token.NOT_EQUAL, Token.LESS, Token.GREATER, Token.LESS_OR_EQUAL, Token.GREATER_OR_EQUAL),
            (Token.PLUS, Token.MINUS),
            (Token.MULTIPLY, Token.DIVIDE, Token.MODULO),
            (Token.MINUS,),
            (),
        ]
        if level < len(operators):
            # NOT or unary MINUS
            if level == 2 or level == 6:
                unary_operator = operators[level][0]
                count = 0
                accepted = None
                while self.token.type == unary_operator:
                    if accepted is None:
                        accepted = self.accept(unary_operator)
                    else:
                        self.accept(unary_operator)
                    count += 1
                expr = self.expression(level + 1)
                if count % 2 != 0:
                    left = expr
                    expr = ast.Expression()
                    expr.token = accepted
                    expr.left = left
                    expr.unary_operator = unary_operator
            else:
                current_operators = operators[level]
                expr = self.expression(level + 1)
                while self.token.type in current_operators:
                    left = expr
                    expr = ast.Expression()
                    expr.left = left
                    accepted = self.accept(current_operators)
                    expr.token = accepted
                    expr.operator = accepted.type
                    expr.right = self.expression(level + 1)
                    # handle only one comparison operator, not sequence of ones
                    if level == 3:
                        break
            return expr
        else:
            return self.term()

    def term(self):
        # wait for valid token
        valid_tokens = (Token.MINUS, Token.IDENTIFIER, Token.TRUE, Token.INTEGER_LITERAL, Token.SYMBOL_LITERAL,
                        Token.TAPE_LITERAL, Token.LEFT_BRACE, Token.INPUT_BOOLEAN, Token.INPUT_INTEGER,
                        Token.INPUT_SYMBOL, Token.INPUT_TAPE, Token.LEFT_BRACKET)
        if self.token.type not in valid_tokens:
            self.error_expected_token_type(valid_tokens)
            while self.token.type not in valid_tokens:
                self.token = self.lexer.next_token()
                if not self.token:
                    assert False, 'End of program text'

        # identifiers
        if self.token.type == Token.IDENTIFIER:
            term = ast.Identifier()
            term.token = self.token
            term.name = self.token.value
            self.accept(Token.IDENTIFIER)

        # literals
        elif self.token.type in (Token.TRUE, Token.FALSE, Token.INTEGER_LITERAL,
                                 Token.SYMBOL_LITERAL, Token.TAPE_LITERAL):
            term = ast.Literal()
            term.token = self.token
            term.value = self.token.value
            if self.token.type in (Token.TRUE, Token.FALSE):
                term.type = Type.BOOLEAN
            elif self.token.type == Token.INTEGER_LITERAL:
                term.type = Type.INTEGER
            elif self.token.type == Token.SYMBOL_LITERAL:
                term.type = Type.SYMBOL
            elif self.token.type == Token.TAPE_LITERAL:
                term.type = Type.TAPE
            self.accept(self.token.type)

        # turing machine literal
        elif self.token.type == Token.LEFT_BRACE:
            term = self.turing_machine_literal()

        # input statements
        elif self.token.type in (Token.INPUT_BOOLEAN, Token.INPUT_INTEGER, Token.INPUT_SYMBOL, Token.INPUT_TAPE):
            term = ast.InputStatement()
            term.token = self.token
            if self.token.type == Token.INPUT_BOOLEAN:
                term.type = Type.BOOLEAN
            elif self.token.type == Token.INPUT_INTEGER:
                term.type = Type.INTEGER
            elif self.token.type == Token.INPUT_SYMBOL:
                term.type = Type.SYMBOL
            elif self.token.type == Token.INPUT_TAPE:
                term.type = Type.TAPE
            self.accept(self.token.type)

        # subexpression in parentheses
        elif self.token.type == Token.LEFT_BRACKET:
            self.accept(Token.LEFT_BRACKET)
            term = self.expression()
            self.accept(Token.RIGHT_BRACKET)

        #### after handling term:
        # handle term[] and term[expression]
        if self.token.type == Token.LEFT_SQUARE_BRACKET:
            left = term
            term = ast.Expression()
            term.left = left
            term.token = self.token
            term.unary_operator = self.token.type
            self.accept(Token.LEFT_SQUARE_BRACKET)
            if self.token.type != Token.RIGHT_SQUARE_BRACKET:
                term.operator, term.unary_operator = term.unary_operator, None
                term.right = self.expression()
            self.accept(Token.RIGHT_SQUARE_BRACKET)

        # handle term(expression)
        elif self.token.type == Token.LEFT_BRACKET:
            left = term
            term = ast.Expression()
            term.left = left
            term.token = self.token
            term.operator = self.token.type
            self.accept(Token.LEFT_BRACKET)
            term.right = self.expression()
            self.accept(Token.RIGHT_BRACKET)

        # handel term^
        elif self.token.type == Token.HEAD:
            left = term
            term = ast.Expression()
            term.left = left
            term.token = self.token
            term.unary_operator = self.token.type
            self.accept(Token.HEAD)

        return term

    def turing_machine_literal(self):
        # initializing literal
        literal = ast.Literal()
        literal.token = self.accept(Token.LEFT_BRACE)
        literal.type = Type.TURING_MACHINE

        # initial state
        state = ast.Identifier()
        state.type = Type.TURING_MACHINE_STATE
        accepted = self.accept(Token.IDENTIFIER)
        state.token = accepted
        state.name = accepted.value
        literal.initial_state = state

        # blank symbol
        symbol = ast.Literal()
        symbol.type = Type.SYMBOL
        accepted = self.accept(Token.SYMBOL_LITERAL)
        symbol.token = accepted
        symbol.value = accepted.value
        literal.blank_symbol = symbol

        # instructions
        if self.token.type == Token.COLON:
            sequence = ast.TuringMachineInstructionSequence()
            self.accept(Token.COLON)
            while self.token.type != Token.RIGHT_BRACE:
                sequence.instructions.append(self.turing_machine_instruction())
                if self.token.type != Token.RIGHT_BRACE:
                    self.accept(Token.SEMICOLON)
            literal.value = sequence
        self.accept(Token.RIGHT_BRACE)
        return literal

    def turing_machine_instruction_sequence(self):
        sequence = ast.TuringMachineInstructionSequence()
        self.accept(Token.COLON)
        self.accept(Token.NEWLINE)
        self.accept(Token.INDENT)
        while self.token.type != Token.DEDENT:
            sequence.instructions.append(self.turing_machine_instruction())
            self.accept(Token.NEWLINE)
        self.accept(Token.DEDENT)
        return sequence

    def turing_machine_instruction(self):
        instruction = ast.TuringMachineInstruction()

        # left state
        temp = ast.Identifier()
        accepted = self.accept(Token.IDENTIFIER)
        temp.token = accepted
        temp.name = accepted.value
        temp.type = Type.TURING_MACHINE_STATE
        instruction.left_state = temp

        # left symbol
        temp = ast.Literal()
        accepted = self.accept(Token.SYMBOL_LITERAL)
        temp.token = accepted
        temp.value = accepted.value
        temp.type = Type.SYMBOL
        instruction.left_symbol = temp

        self.accept(Token.ASSIGNMENT)

        # right state
        accepted = self.accept((Token.IDENTIFIER, Token.MINUS))
        temp = ast.Identifier()
        temp.token = accepted
        temp.type = Type.TURING_MACHINE_STATE
        if accepted.type == Token.IDENTIFIER:
            temp.name = accepted.value
        elif accepted.type == Token.MINUS:
            temp.name = instruction.left_state.name
        instruction.right_state = temp

        # right symbol
        accepted = self.accept((Token.SYMBOL_LITERAL, Token.MINUS))
        temp = ast.Literal()
        temp.token = accepted
        temp.type = Type.SYMBOL
        if accepted.type == Token.SYMBOL_LITERAL:
            temp.value = accepted.value
        elif accepted.type == Token.MINUS:
            temp.value = instruction.left_symbol.value
        instruction.right_symbol = temp

        # shift
        instruction.shift = self.accept((Token.LESS, Token.GREATER, Token.MINUS)).value
        return instruction
