import collections
import re

from error import generate_error

token_specification = [
    ('COMMENT',                 r'/\*(?:.|\n)*\*/|//.*$'),
    # ('KEYWORD',                 r'|'.join(keyword for keyword in keywords)),
    ('TRUE',                    r'true'),
    ('FALSE',                   r'false'),
    ('AND',                     r'and'),
    ('OR',                      r'or'),
    ('NOT',                     r'not'),
    ('IF',                      r'if'),
    ('ELIF',                    r'elif'),
    ('ELSE',                    r'else'),
    ('WHILE',                   r'while'),
    ('IDENTIFIER',              r'[a-zA-Z_][a-zA-Z_0-9]*'),
    ('INTEGER_LITERAL',         r'-?[0-9]+'),
    ('LEFT_BRACE',              r'\{'),
    ('RIGHT_BRACE',             r'\}'),
    ('LEFT_BRACKET',            r'\('),
    ('RIGHT_BRACKET',           r'\)'),
    ('LEFT_SQUARE_BRACKET',     r'\['),
    ('RIGHT_SQUARE_BRACKET',    r'\]'),
    ('COLON',                   r':'),
    # ('MODIFY_OPERATOR',         r'\+=|-=|\*=|/=|%='),
    ('ASSIGNMENT_PLUS',         r'\+='),
    ('ASSIGNMENT_MINUS',        r'-='),
    ('ASSIGNMENT_MULTIPLY',     r'\*='),
    ('ASSIGNMENT_DIVIDE',       r'/='),
    ('ASSIGNMENT_MODULO',       r'%='),
    # ('ARITHMETIC_OPERATOR',     r'[+\-*/%]'),
    ('PLUS',                    r'\+'),
    ('MINUS',                   r'-'),
    ('MULTIPLY',                r'\*'),
    ('DIVIDE',                  r'/'),
    ('MODULO',                  r'%'),
    # ('CARET_OPERATOR',          r'\^\+|\^-|\^\*|\^/|\^%'),
    ('HEAD_PLUS',               r'\^\+'),
    ('HEAD_MINUS',              r'\^-'),
    ('HEAD_MULTIPLY',           r'\^\*'),
    ('HEAD_DIVIDE',             r'\^/'),
    ('HEAD_MODULO',             r'\^%'),
    # ('INPUT_OPERATOR',          r'>b|>i|>\'|>"'),
    ('INPUT_BOOLEAN',           r'>b'),
    ('INPUT_INTEGER',           r'>i'),
    ('INPUT_SYMBOL',            r">'"),
    ('INPUT_TAPE',              r'>"'),
    # ('OUTPUT_OPERATOR',         r'<b|<i|<\'|<"|<<'),
    ('OUTPUT_BOOLEAN',          r'<b'),
    ('OUTPUT_INTEGER',          r'<i'),
    ('OUTPUT_SYMBOL',           r"<'"),
    ('OUTPUT_TAPE',             r'<"'),
    ('OUTPUT_ANY',              r'<<'),
    ('SYMBOL_LITERAL',          r"'(?:\\.|[^\\'\n])*'"),
    ('TAPE_LITERAL',            r'"(?:\\.|[^\\"\n])*"'),
    # ('COMPARISON_OPERATOR',     r'==|!=|<=|>=|<|>'),
    ('EQUAL',                   r'=='),
    ('NOT_EQUAL',               r'!='),
    ('LESS_OR_EQUAL',           r'<='),
    ('GREATER_OR_EQUAL',        r'>='),
    ('LESS',                    r'<'),
    ('GREATER',                 r'>'),
    # ('ASSIGNMENT_OPERATOR',     r'='),
    ('ASSIGNMENT',              r'='),
    ('BLANK_LINE',              r'^[ \t]*\n'),
    ('LINE_CONTINUATION',       r'\\\n'),
    ('NEWLINE',                 r'\n'),
    ('INDENT',                  r'^[ \t]+'),
    ('BLANK',                   r'[ \t]+'),
    ('UNDEFINED_TOKEN',         r'.'),

    ('END_OF_FILE',             r''),
    ('DEDENT',                  r''),
    ('INDENTATION_ERROR',       r''),
]


class Token:
    (COMMENT, TRUE, FALSE, AND, OR, NOT, IF, ELIF, ELSE, WHILE, IDENTIFIER, INTEGER_LITERAL, LEFT_BRACE, RIGHT_BRACE,
     LEFT_BRACKET, RIGHT_BRACKET, LEFT_SQUARE_BRACKET, RIGHT_SQUARE_BRACKET, COLON, ASSIGNMENT_PLUS, ASSIGNMENT_MINUS,
     ASSIGNMENT_MULTIPLY, ASSIGNMENT_DIVIDE, ASSIGNMENT_MODULO, PLUS, MINUS, MULTIPLY, DIVIDE, MODULO, HEAD_PLUS,
     HEAD_MINUS, HEAD_MULTIPLY, HEAD_DIVIDE, HEAD_MODULO, INPUT_BOOLEAN, INPUT_INTEGER, INPUT_SYMBOL, INPUT_TAPE,
     OUTPUT_BOOLEAN, OUTPUT_INTEGER, OUTPUT_SYMBOL, OUTPUT_TAPE, OUTPUT_ANY, SYMBOL_LITERAL, TAPE_LITERAL, EQUAL,
     NOT_EQUAL, LESS_OR_EQUAL, GREATER_OR_EQUAL, LESS, GREATER, ASSIGNMENT, BLANK_LINE, LINE_CONTINUATION, NEWLINE,
     INDENT, BLANK, UNDEFINED_TOKEN, END_OF_FILE, DEDENT, INDENTATION_ERROR) = [token[0] for token in token_specification]

    def __init__(self, type_, value, line, column):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __bool__(self):
        return self.type != Token.END_OF_FILE

    def __str__(self):
        return 'Token: type={}, value={}, line={}, column={}'.format(
            self.type, repr(self.value), self.line, self.column)


class Lexer:
    token_specification_string = '|'.join('(?P<{}>{})'.format(*spec) for spec in token_specification)
    rg = re.compile(token_specification_string, re.MULTILINE)
    del token_specification_string

    def __init__(self, text):
        self.text = text
        self.token = Token(Token.END_OF_FILE, '', 0, 0)
        self.mo = self.rg.match(self.text)
        self.line_num = 1
        self.line_start = 0
        self.indent_stack = []
        self.dedent_count = 0

    def next_token(self):
        while True:
            if self.dedent_count:
                self.dedent_count -= 1
                self.token = Token(
                    Token.DEDENT, self.indent_stack.pop(),
                    self.line_num, self.mo.start() - self.line_start + 1
                )
                return self.token
            type_ = self.mo.lastgroup
            value = self.mo.group(type_)
            if self.token.type == Token.LINE_CONTINUATION and type_ == Token.INDENT:
                type_ = Token.BLANK
            if self.token and self.token.type == Token.NEWLINE and type_ not in (Token.INDENT, Token.BLANK_LINE):
                if self.indent_stack:
                    self.dedent_count = len(self.indent_stack)
                    continue
            if type_ == Token.INDENT:
                if not self.indent_stack:
                    self.indent_stack.append(value)
                else:
                    last_indent = self.indent_stack[-1]
                    if value == last_indent:
                        type_ = Token.BLANK
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
                            type_ = Token.INDENTATION_ERROR
            self.token = Token(getattr(Token, type_), value, self.line_num, self.mo.start() - self.line_start + 1)
            if type_ in (Token.NEWLINE, Token.LINE_CONTINUATION, Token.BLANK_LINE):
                self.line_start = self.mo.end()
                self.line_num += 1
            if type_ == Token.UNDEFINED_TOKEN:
                generate_error(
                    'Lexer', "Undefined token {}".format(repr(self.token.value)),
                    self.token.line, self.token.column)
            if type_ == Token.INDENTATION_ERROR:
                generate_error('Lexer', 'Indentation error', self.token.line, self.token.column)
            self.mo = self.rg.match(self.text, self.mo.end())
            if type_ not in (Token.BLANK, Token.LINE_CONTINUATION, Token.BLANK_LINE,
                             Token.UNDEFINED_TOKEN, Token.INDENTATION_ERROR, Token.COMMENT):
                return self.token
