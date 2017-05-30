import collections
import re

from error import generate_error


Token = collections.namedtuple('Token', ['type', 'value', 'line', 'column'])


class Lexer:
    # keywords
    keywords = {'true', 'false', 'and', 'or', 'not', 'if', 'elif', 'else', 'while'}

    # tokens
    token_specification = [
        ('COMMENT',                 r'/\*(?:.|\n)*\*/|//.*$'),
        ('KEYWORD',                 r'|'.join(keyword for keyword in keywords)),
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
        ('SYMBOL_LITERAL',          r"'(?:\\.|[^\\'\n])*'"),
        ('TAPE_LITERAL',            r'"(?:\\.|[^\\"\n])*"'),
        ('COMPARISON_OPERATOR',     r'==|!=|<=|>=|<|>'),
        ('ASSIGNMENT_OPERATOR',     r'='),
        ('BLANK_LINE',              r'^[ \t]*\n'),
        ('LINE_CONTINUATION',       r'\\\n'),
        ('NEWLINE',                 r'\n'),
        ('INDENT',                  r'^[ \t]+'),
        ('BLANK',                   r'[ \t]+'),
        ('UNDEFINED_TOKEN',         r'.'),
    ]

    token_specification = '|'.join('(?P<{}>{})'.format(*spec) for spec in token_specification)
    rg = re.compile(token_specification, re.MULTILINE)

    def __init__(self, text):
        self.text = text
        self.token = None
        self.mo = self.rg.match(self.text)
        self.line_num = 1
        self.line_start = 0
        self.indent_stack = []
        self.dedent_count = 0

    def next_token(self):
        while self.mo:
            if self.dedent_count:
                self.dedent_count -= 1
                self.token = Token(
                    'DEDENT', self.indent_stack.pop(),
                    self.line_num, self.mo.start() - self.line_start + 1
                )
                return self.token
            type_ = self.mo.lastgroup
            value = self.mo.group(type_)
            if self.token and self.token.type == 'LINE_CONTINUATION' and type_ == 'INDENT':
                type_ = 'BLANK'
            if self.token and self.token.type == 'NEWLINE' and type_ not in ('INDENT', 'BLANK_LINE'):
                if self.indent_stack:
                    self.dedent_count = len(self.indent_stack)
                    continue
            if type_ == 'INDENT':
                if not self.indent_stack:
                    self.indent_stack.append(value)
                else:
                    last_indent = self.indent_stack[-1]
                    if value == last_indent:
                        type_ = 'BLANK'
                    elif value.startswith(last_indent):
                        self.indent_stack.append(value)
                    else:
                        if last_indent.startswith(value):
                            for idx, indent in enumerate(self.indent_stack):
                                if value == indent:
                                    self.dedent_count = len(self.indent_stack) - idx - 1
                                    break
                        if self.dedent_count:
                            continue
                        else:
                            type_ = 'INDENTATION_ERROR'
            self.token = Token(type_, value, self.line_num, self.mo.start() - self.line_start + 1)
            if type_ in ('NEWLINE', 'LINE_CONTINUATION', 'BLANK_LINE'):
                self.line_start = self.mo.end()
                self.line_num += 1
            if type_ == 'UNDEFINED_TOKEN':
                generate_error(
                    'Lexer', "Undefinded token '{}'".format(self.token.value),
                    self.token.line, self.token.column)
            if type_ == 'INDENTATION_ERROR':
                generate_error('Lexer', 'Indentation error', self.token.line, self.token.column)
            self.mo = self.rg.match(self.text, self.mo.end())
            if type_ not in (
                    'BLANK', 'LINE_CONTINUATION', 'BLANK_LINE', 'UNDEFINED_TOKEN', 'INDENTATION_ERROR'):
                return self.token
        else:
            if self.indent_stack:
                self.token = Token(
                    'DEDENT', self.indent_stack.pop(),
                    self.line_num, 1
                )
                return self.token
            else:
                self.token = None
                return self.token
