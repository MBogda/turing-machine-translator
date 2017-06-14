import re
from typing import Union, List, Tuple

from source.error import generate_error, get_lexer_errors, get_parser_errors
from source import ast
from source.ast import Type
from source.lexer import Token
from source.parser import Parser


class SemanticAnalyzer:

    def __init__(self, program_text: str):
        # self.ast = Parser(program_text).parse()
        try:
            self.ast = Parser(program_text).parse()
        except AssertionError as ex:
            if ex.args[0] == 'End of program text':
                pass
        self.variable_table = {}

    def analyze(self):
        if get_lexer_errors() or get_parser_errors():
            self._analyze(self.ast)
            return self.ast

    @staticmethod
    def incompatible_types_error(token: Token, type1: str, type2: str):
        generate_error('Semantic', 'Incompatible types {} and {}'.format(type1, type2), token.line, token.column)

    @staticmethod
    def invalid_type_error(token: Token, type_: str, expected_type: Union[str, List, Tuple]):
        if isinstance(expected_type, (list, tuple)):
            expected_type = ' or '.join(expected_type)
        generate_error('Semantic', 'Invalid type, expected {}, got {}'.format(expected_type, type_),
                       token.line, token.column)

    @staticmethod
    def undeclared_variable_error(token: Token, variable_name: str):
        generate_error('Semantic', 'Undeclared variable {}'.format(variable_name), token.line, token.column)

    @staticmethod
    def integer_literal_out_of_range_error(token: Token, value: int):
        generate_error('Semantic', 'Integer literal is out of range, should be in [-32768,32767], got {}'.format(value),
                       token.line, token.column)

    @staticmethod
    def symbol_literal_length_error(token: Token, length: int):
        generate_error('Semantic', 'Symbol literal length should be 1, got {}'.format(length), token.line, token.column)

    @staticmethod
    def tape_literal_length_error(token: Token):
        generate_error('Semantic', 'Tape literal length should greater than 0, got 0', token.line, token.column)

    @staticmethod
    def tape_literal_multile_heads_error(token: Token, head_count: int):
        generate_error('Semantic', 'Number of heads should be 0 or 1, got {}'.format(head_count),
                       token.line, token.column)

    def _analyze(self, node):
        # debug: check for handling all tokens:
        # if getattr(node, 'token', 0) is None:
        #     print('Undefined token!', node)
        # elif getattr(node, 'token', 0) != 0:
        #     if not isinstance(node.token, Token):
        #         print('Bad token')
        if isinstance(node, ast.InstructionSequence):
            for instr in node.instructions:
                self._analyze(instr)

        elif isinstance(node, ast.IfStatement):
            self._analyze(node.condition)
            if node.condition.type != Type.BOOLEAN:
                self.invalid_type_error(node.condition.token, node.condition.type, Type.BOOLEAN)
            self._analyze(node.if_body)
            if node.else_body is not None:
                self._analyze(node.else_body)

        elif isinstance(node, ast.WhileStatement):
            self._analyze(node.condition)
            if node.condition.type != Type.BOOLEAN:
                self.invalid_type_error(node.condition.token, node.condition.type, Type.BOOLEAN)
            self._analyze(node.body)

        elif isinstance(node, ast.OutputStatement):
            self._analyze(node.value)
            if node.type and node.type != node.value.type:
                self.invalid_type_error(node.value.token, node.value.type, node.type)
            elif node.type is None:
                node.type = node.value.type

        elif isinstance(node, ast.AssignmentStatement):
            # always analyze right side
            self._analyze(node.right)
            if node.operator == Token.COLON:
                # node.left is only ast.Identifier and node.right is only
                # ast.TuringMachineInstructionSequence according to the parser
                identifier = node.left
                self._analyze(identifier)
                if identifier.type != Type.TURING_MACHINE:
                    self.invalid_type_error(identifier.token, identifier.type, Type.TURING_MACHINE)
            else:
                if isinstance(node.left, ast.Identifier):
                    identifier = node.left
                    if node.operator == Token.ASSIGNMENT and identifier.name not in self.variable_table:
                        self.variable_table[identifier.name] = node.right.type
                    else:
                        self._analyze(identifier)
                        if identifier.type != node.right.type:
                            self.incompatible_types_error(node.token, identifier.type, node.right.type)
                else:
                    self._analyze(node.left)
                    if node.left.type != node.right.type:
                        self.incompatible_types_error(node.token, node.left.type, node.right.type)

        elif isinstance(node, ast.Expression):
            self._analyze(node.left)
            # unary operator
            if node.unary_operator:
                operator = node.unary_operator
                # not
                if operator == Token.NOT:
                    node.type = Type.BOOLEAN
                    if node.left.type != Type.BOOLEAN:
                        self.invalid_type_error(node.left.token, node.left.type, Type.BOOLEAN)
                # -
                elif operator == Token.MINUS:
                    node.type = Type.INTEGER
                    if node.left.type != Type.INTEGER:
                        self.invalid_type_error(node.left.token, node.left.type, Type.INTEGER)
                # ^
                elif operator == Token.HEAD:
                    node.type = Type.INTEGER
                    if node.left.type != Type.TAPE:
                        self.invalid_type_error(node.left.token, node.left.type, Type.TAPE)
                # []
                elif operator == Token.LEFT_SQUARE_BRACKET:
                    node.type = Type.INTEGER
                    if node.left.type != Type.TAPE:
                        self.invalid_type_error(node.left.token, node.left.type, Type.TAPE)
                # wrong state, need to fix program
                else:
                    assert False, 'Unhandled unary operator!'

            # binary operator
            elif node.operator:
                self._analyze(node.right)
                operator = node.operator
                # or, and
                if operator in (Token.OR, Token.AND):
                    node.type = Type.BOOLEAN
                    if node.left.type != node.right.type:
                        self.incompatible_types_error(node.token, node.left.type, node.right.type)
                    if node.left.type != Type.BOOLEAN:
                        self.invalid_type_error(node.left.token, node.left.type, Type.BOOLEAN)
                    if node.right.type != Type.BOOLEAN:
                        self.invalid_type_error(node.right.token, node.right.type, Type.BOOLEAN)
                # ==, !=
                elif operator in (Token.EQUAL, Token.NOT_EQUAL):
                    node.type = Type.BOOLEAN
                    if node.left.type != node.right.type:
                        self.incompatible_types_error(node.token, node.left.type, node.right.type)
                    if node.left.type not in (Type.INTEGER, Type.SYMBOL, Type.TAPE):
                        self.invalid_type_error(node.left.token, node.left.type, (Type.INTEGER, Type.SYMBOL, Type.TAPE))
                    if node.right.type not in (Type.INTEGER, Type.SYMBOL, Type.TAPE):
                        self.invalid_type_error(node.right.token, node.right.type, (Type.INTEGER, Type.SYMBOL, Type.TAPE))
                # <, >, <=, >=
                elif operator in (Token.LESS, Token.GREATER, Token.LESS_OR_EQUAL, Token.GREATER_OR_EQUAL):
                    node.type = Type.BOOLEAN
                    if node.left.type != node.right.type:
                        self.incompatible_types_error(node.token, node.left.type, node.right.type)
                    if node.left.type != Type.INTEGER:
                        self.invalid_type_error(node.left.token, node.left.type, Type.INTEGER)
                    if node.right.type != Type.INTEGER:
                        self.invalid_type_error(node.right.token, node.right.type, Type.INTEGER)
                # +
                elif operator == Token.PLUS:
                    node.type = node.left.type
                    if node.left.type != node.right.type:
                        self.incompatible_types_error(node.token, node.left.type, node.right.type)
                    if node.left.type not in (Type.INTEGER, Type.TAPE, Type.TURING_MACHINE):
                        self.invalid_type_error(node.left.token, node.left.type,
                                                (Type.INTEGER, Type.TAPE, Type.TURING_MACHINE))
                        node.type = node.right.type
                    if node.right.type not in (Type.INTEGER, Type.TAPE, Type.TURING_MACHINE):
                        self.invalid_type_error(node.right.token, node.right.type,
                                                (Type.INTEGER, Type.TAPE, Type.TURING_MACHINE))
                        if node.type == node.right.type:
                            node.type = Type.INTEGER
                # -
                elif operator == Token.MINUS:
                    node.type = node.left.type
                    if node.left.type != node.right.type:
                        self.incompatible_types_error(node.token, node.left.type, node.right.type)
                    if node.left.type not in (Type.INTEGER, Type.TAPE):
                        self.invalid_type_error(node.left.token, node.left.type, (Type.INTEGER, Type.TAPE))
                        node.type = node.right.type
                    if node.right.type not in (Type.INTEGER, Type.TAPE):
                        self.invalid_type_error(node.right.token, node.right.type, (Type.INTEGER, Type.TAPE))
                        if node.type == node.right.type:
                            node.type = Type.INTEGER
                # *, /, %
                elif operator in (Token.MULTIPLY, Token.DIVIDE, Token.MODULO):
                    node.type = Type.INTEGER
                    if node.left.type != node.right.type:
                        self.incompatible_types_error(node.token, node.left.type, node.right.type)
                    if node.left.type != Type.INTEGER:
                        self.invalid_type_error(node.left.token, node.left.type, Type.INTEGER)
                    if node.right.type != Type.INTEGER:
                        self.invalid_type_error(node.right.token, node.right.type, Type.INTEGER)
                # tape[integer]
                elif operator == Token.LEFT_SQUARE_BRACKET:
                    node.type = Type.SYMBOL
                    if node.left.type != Type.TAPE:
                        self.invalid_type_error(node.left.token, node.left.type, Type.TAPE)
                    if node.right.type != Type.INTEGER:
                        self.invalid_type_error(node.right.token, node.right.type, Type.INTEGER)
                # turing_machine(tape)
                elif operator == Token.LEFT_BRACKET:
                    node.type = Type.TAPE
                    if node.left.type != Type.TURING_MACHINE:
                        self.invalid_type_error(node.left.token, node.left.type, Type.TURING_MACHINE)
                    if node.right.type != Type.TAPE:
                        self.invalid_type_error(node.right.token, node.right.type, Type.TAPE)
                # wrong state, need to fix program
                else:
                    assert False, 'Unhandled binary operator!'

            # wrong state, need to fix program
            else:
                assert False, 'Neither unary nor binary operator exists in expression'

        elif isinstance(node, ast.Identifier):
            if node.name not in self.variable_table:
                self.undeclared_variable_error(node.token, node.name)
            else:
                node.type = self.variable_table[node.name]

        elif isinstance(node, ast.Literal):
            if node.type == Type.BOOLEAN:
                # todo: bad practice: tokens TRUE and FALSE defined in the lexer but definition used here
                if node.value == 'true':
                    node.value = True
                elif node.value == 'false':
                    node.value = False
                # wrong state, need to fix program
                else:
                    assert False, 'Unknown boolean type'
            elif node.type == Type.INTEGER:
                node.value = int(node.value)
                # if -32768 > node.value < 32767:
                if -2 ** 15 > node.value < 2 ** 15 - 1:
                    self.integer_literal_out_of_range_error(node.token, node.value)
            elif node.type == Type.SYMBOL:
                # remove quotes
                node.value = node.value[1:-1]
                # replace escaped characters
                node.value = re.sub(
                    r"\\\\|\\n|\\t|\\'",
                    lambda mo: {r'\\': '\\', r'\n': '\n', r'\t': '\t', r"'": "'"}[mo.group],
                    node.value,
                )

                if len(node.value) != 1:
                    self.symbol_literal_length_error(node.token, len(node.value))
            elif node.type == Type.TAPE:
                # remove quotes
                node.value = node.value[1:-1]

                if len(node.value) == 0:
                    self.tape_literal_length_error(node.token)
                head_count = node.value.count('^') - node.value.count(r'\^')
                if head_count > 1:
                    self.tape_literal_multile_heads_error(node.token, head_count)

                # todo: handle this situation: "\\\^a^"
                # Replace escaped characters and replace \^ with ^ and ^ with \^
                node.value = re.sub(
                    r'\\\\|\\n|\\t|\\|\\\^|\^"',
                    lambda mo: {r'\\': '\\', r'\n': '\n', r'\t': '\t', r'"': '"', r'\^': r'^', r'^': r'\^'}[mo.group],
                    node.value,
                )
                # Find index of \^ and replace it with ''
                idx = node.value.find('\^')
                if idx == -1:
                    idx = 0
                node.value = node.value.replace('\^', '')

                node.value = [idx, list(node.value)]
            elif node.type == Type.TURING_MACHINE:
                # todo: create tm intermediate representation
                self._analyze(node.blank_symbol)
                if node.value is not None:
                    self._analyze(node.value)
            # wrong state, need to fix program
            else:
                assert False, 'Unknown literal type'

        elif isinstance(node, ast.InputStatement):
            pass

        elif isinstance(node, ast.TuringMachineInstructionSequence):
            for instr in node.instructions:
                self._analyze(instr)
                node.states.add(instr.left_state)
                node.states.add(instr.right_state)
                node.symbols.add(instr.left_symbol)
                node.symbols.add(instr.right_symbol)

        elif isinstance(node, ast.TuringMachineInstruction):
            self._analyze(node.left_symbol)
            self._analyze(node.right_symbol)

        # wrong state, need to fix program
        else:
            assert False, 'Unknown AST node'
