# Nodes of Abstract Syntax Tree
# todo: annotate all types
# todo: more pretty printing (like tree in linux)
# todo? initialize all params in __init__
# todo? add tokens to all ast nodes
from typing import List


class Type:
    (BOOLEAN, INTEGER, SYMBOL, TAPE,
     TURING_MACHINE, TURING_MACHINE_STATE) = ('BOOLEAN', 'INTEGER', 'SYMBOL', 'TAPE',
                                              'TURING_MACHINE', 'TURING_MACHINE_STATE')


class InstructionSequence:
    def __init__(self):
        # self.instructions: List[Union[IfStatement, WhileStatement, OutputStatement, AssignmentStatement]] = []
        self.instructions = []

    def __str__(self):
        return self.pretty_str()

    def pretty_str(self, depth=0):
        res_str = '\n{}InstructionSequence:'.format('│' * (depth - 1) + '├' if depth > 0 else '')
        for instr in self.instructions:
            res_str += instr.pretty_str(depth + 1)
        return res_str


class IfStatement:
    def __init__(self):
        self.condition = None
        self.if_body = None
        self.else_body = None

    def __str__(self):
        return self.pretty_str()

    def pretty_str(self, depth=0):
        return '\n{0}IfStatement:\n│{1}condition:{3}\n│{1}if_body:{4}\n│{2}else_body:{5}'.format(
            '│' * (depth - 1) + '├' if depth > 0 else '',
            '│' * (depth - 1) + '├' if depth > 0 else '',
            '│' * (depth - 1) + '└' if depth > 0 else '',
            self.condition.pretty_str(depth + 2),
            self.if_body.pretty_str(depth + 2),
            self.else_body.pretty_str(depth + 2) if self.else_body is not None else None,
        )


class WhileStatement:
    def __init__(self):
        self.condition = None
        self.body = None

    def __str__(self):
        return self.pretty_str()

    def pretty_str(self, depth=0):
        return '\n{0}WhileStatement:\n│{1}condition:{3}\n│{2}body:{4}'.format(
            '│' * (depth - 1) + '├' if depth > 0 else '',
            '│' * (depth - 1) + '├' if depth > 0 else '',
            '│' * (depth - 1) + '└' if depth > 0 else '',
            self.condition.pretty_str(depth + 2),
            self.body.pretty_str(depth + 2),
        )


class OutputStatement:
    def __init__(self):
        self.token = None
        self.type = None
        self.value = None

    def __str__(self):
        return self.pretty_str()

    def pretty_str(self, depth=0):
        return '\n{0}OutputStatement:\n│{1}type={3}\n│{2}value:{4}'.format(
            '│' * (depth - 1) + '├' if depth > 0 else '',
            '│' * (depth - 1) + '├' if depth > 0 else '',
            '│' * (depth - 1) + '└' if depth > 0 else '',
            self.type,
            self.value.pretty_str(depth + 2),
        )


class AssignmentStatement:
    def __init__(self):
        self.token = None
        self.operator = None
        self.left = None
        self.right = None

    def __str__(self):
        return self.pretty_str()

    def pretty_str(self, depth=0):
        return '\n{0}AssignmentStatement:\n│{1}operator={3}\n│{1}left:{4}\n│{2}right:{5}'.format(
            '│' * (depth - 1) + '├' if depth > 0 else '',
            '│' * (depth - 1) + '├' if depth > 0 else '',
            '│' * (depth - 1) + '└' if depth > 0 else '',
            self.operator,
            self.left.pretty_str(depth + 2),
            self.right.pretty_str(depth + 2),
        )


class Expression:
    def __init__(self):
        self.token = None
        self.operator = None
        self.unary_operator = None
        self.type = None
        self.left = None
        self.right = None

    def __str__(self):
        return self.pretty_str()

    def pretty_str(self, depth=0):
        return '\n{0}Expression:\n│{1}operator={3}\n│{2}unary_operator={4}' \
               '\n│{1}type={4}\n│{1}left:{5}\n│{1}right:{6}'.format(
            '│' * (depth - 1) + '├' if depth > 0 else '',
            '│' * (depth - 1) + '├' if depth > 0 else '',
            '│' * (depth - 1) + '└' if depth > 0 else '',
            self.operator,
            self.unary_operator,
            self.type,
            self.left.pretty_str(depth + 2),
            self.right.pretty_str(depth + 2) if self.right is not None else None,
        )


class Identifier:
    def __init__(self):
        self.token = None
        self.name = None
        self.type = None

    def __str__(self):
        return self.pretty_str()

    def pretty_str(self, depth=0):
        return '\n{0}Identifier:\n│{1}name={3}\n│{2}type={4}'.format(
            '│' * (depth - 1) + '├' if depth > 0 else '',
            '│' * (depth - 1) + '├' if depth > 0 else '',
            '│' * (depth - 1) + '└' if depth > 0 else '',
            self.name,
            self.type,
        )


class Literal:
    def __init__(self):
        self.token = None
        self.value = None
        self.type = None
        self.initial_state = None
        self.blank_symbol = None

    def __str__(self):
        return self.pretty_str()

    def pretty_str(self, depth=0):
        return '\n{0}Literal:\n│{1}type={3}\n│{1}initial_state:{4}\n│{1}blank_symbol:{5}\n│{2}value:{6}'.format(
            '│' * (depth - 1) + '├' if depth > 0 else '',
            '│' * (depth - 1) + '├' if depth > 0 else '',
            '│' * (depth - 1) + '└' if depth > 0 else '',
            self.type,
            self.initial_state.pretty_str(depth + 2) if self.initial_state is not None else None,
            self.blank_symbol.pretty_str(depth + 2) if self.initial_state is not None else None,
            self.value.pretty_str(depth + 2)
            if isinstance(self.initial_state, TuringMachineInstructionSequence)
            else self.value,
        )


class InputStatement:
    def __init__(self):
        self.type = None

    def __str__(self):
        return self.pretty_str()

    def pretty_str(self, depth=0):
        return '\n{0}InputStatement:\n│{2}type={3}'.format(
            '│' * (depth - 1) + '├' if depth > 0 else '',
            '│' * (depth - 1) + '├' if depth > 0 else '',
            '│' * (depth - 1) + '└' if depth > 0 else '',
            self.type,
        )


class TuringMachineInstructionSequence:
    def __init__(self):
        self.instructions: List[TuringMachineInstruction] = []
        self.states = set()
        self.symbols = set()

    def __str__(self):
        return self.pretty_str()

    def pretty_str(self, depth=0):
        res_str = '\n{0}TuringMachineInstructionSequence:\n│{1}states={3}\n│{2}symbols={4}'.format(
            '│' * (depth - 1) + '├' if depth > 0 else '',
            '│' * (depth - 1) + '├' if depth > 0 else '',
            '│' * (depth - 1) + '└' if depth > 0 else '',
            self.states,
            self.symbols,
        )
        for tm_instr in self.instructions:
            res_str += tm_instr.pretty_str(depth + 1)
        return res_str


class TuringMachineInstruction:
    def __init__(self):
        self.left_state = None
        self.left_symbol = None
        self.right_state = None
        self.right_symbol = None
        self.shift = None

    def __str__(self):
        return self.pretty_str()

    def pretty_str(self, depth=0):
        return '\n{0}TuringMachineInstruction:\n│{1}left_state:{3}\n│{1}left_symbol:{4}' \
               '\n│{1}right_state:{5}\n│{1}right_symbol:{6}\n│{2}shift={7}'.format(
            '│' * (depth - 1) + '├' if depth > 0 else '',
            '│' * (depth - 1) + '├' if depth > 0 else '',
            '│' * (depth - 1) + '└' if depth > 0 else '',
            self.left_state.pretty_str(depth + 2),
            self.left_symbol.pretty_str(depth + 2),
            self.right_state.pretty_str(depth + 2),
            self.right_symbol.pretty_str(depth + 2),
            self.shift,
        )
