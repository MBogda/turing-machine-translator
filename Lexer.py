import collections
import re


Token = collections.namedtuple('Token', ['type', 'value', 'line', 'column'])


class Lexer:
    # keywords
    keywords = {'true', 'false', 'and', 'or', 'not', 'if', 'elif', 'else', 'while'}

    # tokens
    token_specification = [
        ('COMMENT',                 r'/\*(?:.|\n)*\*/|//.*$'),
        ('IDENTIFIER',              r'[a-zA-Z_][a-zA-Z_0-9]*'),
        ('INTEGER_LITERAL',         r'-?[0-9]+'),
        ('LEFT_BRACE',              r'\{'),
        ('RIGHT_BRACE',             r'\}'),
        ('LEFT_BRACKET',            r'\('),
        ('RIGHT_BRACKET',           r'\)'),
        ('LEFT_SQUARE_BRACKET',     r'\['),
        ('RIGHT_SQUARE_BRACKET',    r'\]'),
        ('COLON',                   r':'),
        ('MODIFY_OPERATOR',         r'\+=|-=|\*=|/=|%='),
        ('ARITHMETIC_OPERATOR',     r'[+\-*/%]'),
        ('CARET_OPERATOR',          r'\^\+|\^-|\^\*|\^/|\^%'),
        ('INPUT_OPERATOR',          r'>b|>i|>\'|>"'),
        ('OUTPUT_OPERATOR',         r'<b|<i|<\'|<"|<<'),
        ('SYMBOL_LITERAL',          r"'(?:\\.|[^\\'])*'"),
        ('TAPE_LITERAL',            r'"(?:\\.|[^\\"])*"'),
        ('COMPARISON_OPERATOR',     r'==|!=|<=|>=|<|>'),
        ('ASSIGNMENT_OPERATOR',     r'='),
        ('NEWLINE',                 r'\n'),
        ('INDENT',                  r'^[ \t]+'),
        ('BLANK',                   r'[ \t]+'),
        ('UNDEFINED',               r'.'),
    ]

    token_specification = '|'.join('(?P<{}>{})'.format(*spec) for spec in token_specification)
    rg = re.compile(token_specification, re.MULTILINE)

    def __init__(self, text):
        self.text = text
        self.token = None
        self.mo = self.rg.match(self.text)
        self.line_num = 1
        self.line_start = 0

    def next_token(self):
        if self.mo:
            type_ = self.mo.lastgroup
            value = self.mo.group(type_)
            if type_ == 'NEWLINE':
                self.line_start = self.mo.end()
                self.line_num += 1
            self.token = Token(type_, value, self.line_num, self.mo.start() - self.line_start + 1)
            self.mo = self.rg.match(self.text, self.mo.end())
        else:
            self.token = None
