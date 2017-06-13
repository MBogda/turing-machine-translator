# Nodes of Abstract Syntax Tree
# todo: annotate all types
# todo: more beautiful printing (like tree in linux)
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
        res_str = '\nInstructionSequence:'
        for instr in self.instructions:
            res_str += str(instr).replace('\n', '\n ')
        return res_str


class IfStatement:
    def __init__(self):
        self.condition = None
        self.if_body = None
        self.else_body = None

    def __str__(self):
        return '\nIfStatement:\n condition:{}\n if_body:{}\n else_body:{}'.format(
            str(self.condition).replace('\n', '\n  '),
            str(self.if_body).replace('\n', '\n  '),
            str(self.else_body).replace('\n', '\n  '),
        )


class WhileStatement:
    def __init__(self):
        self.condition = None
        self.body = None

    def __str__(self):
        return '\nWhileStatement:\n condition:{}\n body:{}'.format(
            str(self.condition).replace('\n', '\n  '),
            str(self.body).replace('\n', '\n  '),
        )


class OutputStatement:
    def __init__(self):
        self.token = None
        self.type = None
        self.value = None

    def __str__(self):
        return '\nOutputStatement:\n type={}\n value:{}'.format(
            self.type,
            str(self.value).replace('\n', '\n  '),
        )


class AssignmentStatement:
    def __init__(self):
        self.token = None
        self.operator = None
        self.left = None
        self.right = None

    def __str__(self):
        return '\nAssignmentStatement:\n operator={}\n left:{}\n right:{}'.format(
            self.operator,
            str(self.left).replace('\n', '\n  '),
            str(self.right).replace('\n', '\n  '),
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
        return '\nExpression:\n operator={}\n unary_operator={}\n type={}\n left:{}\n right:{}'.format(
            self.operator,
            self.unary_operator,
            self.type,
            str(self.left).replace('\n', '\n  '),
            str(self.right).replace('\n', '\n  '),
        )


class Identifier:
    def __init__(self):
        self.token = None
        self.name = None
        self.type = None

    def __str__(self):
        return '\nIdentifier:\n name={}\n type={}'.format(
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
        return '\nLiteral:\n type={}\n initial_state:{}\n blank_symbol:{}\n value:{}'.format(
            self.type,
            str(self.initial_state).replace('\n', '\n  '),
            str(self.blank_symbol).replace('\n', '\n  '),
            str(self.value).replace('\n', '\n  '),
        )


class InputStatement:
    def __init__(self):
        self.type = None

    def __str__(self):
        return '\nInputStatement:\n type={}'.format(self.type)


class TuringMachineInstructionSequence:
    def __init__(self):
        self.instructions: List[TuringMachineInstruction] = []
        self.states = set()
        self.symbols = set()

    def __str__(self):
        res_str = '\nTuringMachineInstructionSequence:\n states={}\n symbols={}'.format(
            self.states,
            self.symbols,
        )
        for instr in self.instructions:
            res_str += str(instr).replace('\n', '\n ')
        return res_str


class TuringMachineInstruction:
    def __init__(self):
        self.left_state = None
        self.left_symbol = None
        self.right_state = None
        self.right_symbol = None
        self.shift = None

    def __str__(self):
        return '\nTuringMachineInstruction:\n left_state:{}\n left_symbol:{}' \
               '\n right_state:{}\n right_symbol:{}\n shift={}'.format(
            str(self.left_state).replace('\n', '\n  '),
            str(self.left_symbol).replace('\n', '\n  '),
            str(self.right_state).replace('\n', '\n  '),
            str(self.right_symbol).replace('\n', '\n  '),
            self.shift,
        )
