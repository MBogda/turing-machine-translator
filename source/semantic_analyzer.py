import re

from source import ast
from source.ast import Type
from source.lexer import Token


class SemanticAnalyzer:

    def __init__(self, program_ast):
        self.ast = program_ast
        self.variable_table = {}

    def analyze(self):
        self._analyze(self.ast)

    # todo:
    def type_error(self):
        print('type error')

    # todo:
    def undeclared_variable_error(self):
        print('undeclared variable error')

    # todo:
    def integer_literal_out_of_range_error(self):
        print('integer out of range error')

    # todo:
    def symbol_literal_length_error(self):
        print('symbol length error')

    # todo:
    def tape_literal_length_error(self):
        print('tape length error')

    # todo:
    def tape_literal_multile_heads_error(self):
        print('tape multiple heads error')

    def _analyze(self, node):
        if isinstance(node, ast.InstructionSequence):
            for instr in node.instructions:
                self._analyze(instr)

        elif isinstance(node, ast.IfStatement):
            self._analyze(node.condition)
            if node.condition.type != Type.BOOLEAN:
                self.type_error()
            self._analyze(node.if_body)
            if node.else_body is not None:
                self._analyze(node.else_body)

        elif isinstance(node, ast.WhileStatement):
            self._analyze(node.condition)
            if node.condition.type != Type.BOOLEAN:
                self.type_error()
            self._analyze(node.body)

        elif isinstance(node, ast.OutputStatement):
            self._analyze(node.value)
            if node.value.type != node.type:
                self.type_error()

        elif isinstance(node, ast.AssignmentStatement):
            self._analyze(node.right)
            if node.operator == Token.COLON:
                # node.right is only ast.Identifier and node.left is only
                # ast.TuringMachineInstructionSequence according to the parser
                identifier = node.left
                self._analyze(identifier)
                if identifier.type != Type.TURING_MACHINE:
                    self.type_error()
            else:
                if isinstance(node.left, ast.Identifier):
                    identifier = node.left
                    if node.operator == Token.ASSIGNMENT and identifier.name not in self.variable_table:
                        self.variable_table[identifier.name] = node.right.type
                    elif identifier.name not in self.variable_table:
                        self.undeclared_variable_error()
                    elif identifier.type != node.right.type:
                        self.type_error()
                else:
                    self._analyze(node.left)
                    if node.left.type != node.right.type:
                        self.type_error()

        elif isinstance(node, ast.Expression):
            self._analyze(node.left)
            # unary operator
            if node.unary_operator:
                operator = node.unary_operator
                # not
                if operator == Token.NOT:
                    if node.left.type != Type.BOOLEAN:
                        self.type_error()
                    node.type = Type.BOOLEAN
                # -
                elif operator == Token.MINUS:
                    if node.left.type != Type.INTEGER:
                        self.type_error()
                    node.type = Type.INTEGER
                # ^
                elif operator == Token.HEAD:
                    if node.left.type != Type.TAPE:
                        self.type_error()
                    node.type = Type.INTEGER
                # []
                elif operator == Token.LEFT_SQUARE_BRACKET:
                    if node.left.type != Type.TAPE:
                        self.type_error()
                    node.type = Type.INTEGER
                # wrong state, need to fix program
                else:
                    assert False, 'Unhandled unary operator!'

            # binary operator
            elif node.operator:
                self._analyze(node.right)
                operator = node.operator
                # or, and
                if operator in (Token.OR, Token.AND):
                    if not node.left.type == node.right.type == Type.BOOLEAN:
                        self.type_error()
                    node.type = Type.BOOLEAN
                # ==, !=
                elif operator in (Token.EQUAL, Token.NOT_EQUAL):
                    if not node.left.type == node.right.type in (Type.INTEGER, Type.SYMBOL, Type.TAPE):
                        self.type_error()
                    node.type = Type.BOOLEAN
                # <, >, <=, >=
                elif operator in (Token.LESS, Token.GREATER, Token.LESS_OR_EQUAL, Token.GREATER_OR_EQUAL):
                    if not node.left.type == node.right.type == Type.INTEGER:
                        self.type_error()
                    node.type = Type.BOOLEAN
                # +, -
                elif operator in (Token.PLUS, Token.MINUS):
                    # todo: smarter type analyzing (e.g. TAPE + BOOLEAN = TAPE)
                    if not node.left.type == node.right.type in (Type.INTEGER, Type.TAPE):
                        self.type_error()
                        node.type = Type.INTEGER
                    else:
                        node.type = node.left.type
                # *, /, %
                elif operator in (Token.MULTIPLY, Token.DIVIDE, Token.MODULO):
                    if not node.left.type == node.right.type == Type.INTEGER:
                        self.type_error()
                    node.type = Type.INTEGER
                # tape[integer]
                elif operator == Token.LEFT_SQUARE_BRACKET:
                    if node.left.type != Type.TAPE or node.right.type != Type.INTEGER:
                        self.type_error()
                    node.type = Type.SYMBOL
                # turing_machine(tape)
                elif operator == Token.LEFT_BRACKET:
                    if node.left.type != Type.TURING_MACHINE or node.right.type != Type.TAPE:
                        self.type_error()
                    node.type = Type.TAPE
                # wrong state, need to fix program
                else:
                    assert False, 'Unhandled binary operator!'

            # wrong state, need to fix program
            else:
                assert False, 'Neither unary nor binary operator exists in expression'

        elif isinstance(node, ast.Identifier):
            if node.name not in self.variable_table:
                self.undeclared_variable_error()
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
                    self.integer_literal_out_of_range_error()
            elif node.type == Type.SYMBOL:
                if len(node.value) != 1:
                    self.symbol_literal_length_error()
                node.value = node.value.replace(r'\\', '\\').replace(
                    r'\n', '\n').replace(r'\t', '\t').replace(r"\'", "'")
            elif node.type == Type.TAPE:
                if len(node.value) == 0:
                    self.tape_literal_length_error()
                if node.value.count('^') - node.value.count(r'\^') > 1:
                    self.tape_literal_multile_heads_error()

                # todo: handle this situation: "\\\^a^"
                # First replace escaped characters
                node.value = node.value.replace(r'\\', '\\').replace(
                    r'\n', '\n').replace(r'\t', '\t').replace(r'\"', '"')
                # then replace \^ with ^ and ^ with \^
                node.value = re.sub(r'\\\^|\^', lambda mo: {r'\^': r'^', r'^': r'\^'}[mo.group()], node.value)
                # and finally find index of \^ and replace it with ''
                idx = node.value.find('\^')
                if idx == -1:
                    idx = 0
                node.value = node.value.replace('\^', '')

                node.value = [idx, list(node.value)]
            elif node.type == Type.TURING_MACHINE:
                # todo: create tm intermediate representation
                pass
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
