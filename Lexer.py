class Lexer:
    # tokens
    tokens = [
        'IDENTIFIER', 'INTEGER_LITERAL', 'SYMBOL_LITERAL', 'TAPE_LITERAL',
        'TRUE', 'FALSE',
        'LEFT_BRACE', 'RIGHT_BRACE', 'LEFT_BRACKET', 'RIGHT_BRACKET', 'LEFT_SQUARE_BRACKET', 'RIGHT_SQUARE_BRACKET',
        'COLON',
        'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'MODULO',
        'CARET_PLUS', 'CARET_MINUS', 'CARET_MULTIPLY', 'CARET_DIVIDE', 'CARET_MODULO',
        'EQUAL', 'NOT_EQUAL', 'LESS', 'GREATER', 'LESS_OR_EQUAL', 'GREATER_OR_EQUAL',
        'ASSIGNMENT', 'PLUS_ASSIGNMENT', 'MINUS_ASSIGNMENT',
        'MULTIPLY_ASSIGNMENT', 'DIVIDE_ASSIGNMENT', 'MODULO_ASSIGNMENT',
        'AND', 'OR', 'NOT',
        'IF', 'ELIF', 'ELSE', 'WHILE',
        'INDENT', 'DEDENT',
        'INPUT', 'OUTPUT',
        'NEW_LINE', 'EOF', 'ERROR',
    ]

    (
        IDENTIFIER, INTEGER_LITERAL, SYMBOL_LITERAL, TAPE_LITERAL,  # todo
        TRUE, FALSE,
        LEFT_BRACE, RIGHT_BRACE, LEFT_BRACKET, RIGHT_BRACKET, LEFT_SQUARE_BRACKET, RIGHT_SQUARE_BRACKET,
        COLON,
        PLUS, MINUS, MULTIPLY, DIVIDE, MODULO,
        CARET_PLUS, CARET_MINUS, CARET_MULTIPLY, CARET_DIVIDE, CARET_MODULO,
        EQUAL, NOT_EQUAL, LESS, GREATER, LESS_OR_EQUAL, GREATER_OR_EQUAL,
        ASSIGNMENT, PLUS_ASSIGNMENT, MINUS_ASSIGNMENT, MULTIPLY_ASSIGNMENT, DIVIDE_ASSIGNMENT, MODULO_ASSIGNMENT,
        AND, OR, NOT,
        IF, ELIF, ELSE, WHILE,
        INDENT, DEDENT, # todo
        INPUT, OUTPUT,
        NEW_LINE, EOF, ERROR,
    ) = range(len(tokens))

    # special symbols
    special_symbols = {
        '{': LEFT_BRACE, '}': RIGHT_BRACE,
        '(': LEFT_BRACKET, ')': RIGHT_BRACKET,
        '[': LEFT_SQUARE_BRACKET, ']': RIGHT_SQUARE_BRACKET,
        ':': COLON,
        '+': PLUS, '-': MINUS, '*': MULTIPLY, '/': DIVIDE, '%': MODULO,
        '^+': CARET_PLUS, '^-': CARET_MINUS, '^*': CARET_MULTIPLY, '^/': CARET_DIVIDE, '^%': CARET_MODULO,
        '==': EQUAL, '!=': NOT_EQUAL, '<': LESS, '>': GREATER, '<=': LESS_OR_EQUAL, '>=': GREATER_OR_EQUAL,
        '=': ASSIGNMENT, '+=': PLUS_ASSIGNMENT, '-=': MINUS_ASSIGNMENT,
        '*=': MULTIPLY_ASSIGNMENT, '/=': DIVIDE_ASSIGNMENT, '%=': MODULO_ASSIGNMENT,
        '>b': INPUT, '>i': INPUT, ">'": INPUT, '>"': INPUT,
        '<b': OUTPUT, '<i': OUTPUT, "<'": OUTPUT, '<"': OUTPUT, '<<': OUTPUT,
    }

    one_char_special_symbols = {symbol for symbol in special_symbols if len(symbol) == 1}
    two_char_special_symbols = {symbol[0] for symbol in special_symbols if len(symbol) == 2}

    # keywords
    keywords = {
        'true': TRUE,
        'false': FALSE,
        'and': AND,
        'or': OR,
        'not': NOT,
        'if': IF,
        'elif': ELIF,
        'else': ELSE,
        'while': WHILE,
    }

    def __init__(self, text):
        self.text = text
        self.index = 0
        self.char = None
        self.category = None
        self.value = None
        self.next_char()

    def next_char(self):
        if self.index >= len(self.text):
            self.char = ''
        else:
            self.char = self.text[self.index]
            self.index += 1

    def next_token(self):
        self.value = None
        self.category = None
        while self.category is None:
            if not self.char:
                self.category = Lexer.EOF
            elif self.char == '\n':
                while self.char == '\n':
                    self.next_char()
                self.category = Lexer.NEW_LINE
            elif self.char.isspace():
                self.next_char()
            elif self.char == '\\':
                self.value = self.char
                self.next_char()
                self.value += self.char
                if self.value != '\\\n':
                    self.category = Lexer.ERROR
                else:
                    self.next_char()
            elif self.char.isdecimal():
                self.value = 0
                while self.char.isdecimal():  # todo: check overflow
                    self.value *= 10
                    self.value += int(self.char)
                    self.next_char()
                self.category = Lexer.INTEGER_LITERAL
            elif self.char.isalpha() or self.char == '_':
                self.value = ''
                while self.char.isalpha() or self.char.isdecimal() or self.char == '_':
                    self.value += self.char
                    self.next_char()
                if self.value in self.keywords:
                    self.category = self.keywords[self.value]
                    self.value = None
                else:
                    self.category = Lexer.IDENTIFIER
            else:
                if self.char not in Lexer.two_char_special_symbols and self.char in Lexer.one_char_special_symbols:
                    self.category = Lexer.special_symbols[self.char]
                    self.next_char()
                elif self.char in Lexer.two_char_special_symbols and self.char in Lexer.one_char_special_symbols:
                    self.value = self.char
                    self.next_char()
                    self.value += self.char
                    if self.value in Lexer.special_symbols:
                        self.category = Lexer.special_symbols[self.value]
                        if not (self.category == Lexer.INPUT or self.category == Lexer.OUTPUT):
                            self.value = None
                        self.next_char()
                    else:
                        self.category = Lexer.special_symbols[self.value[0]]
                        self.value = None
                elif self.char in Lexer.two_char_special_symbols:
                    self.value = self.char
                    self.next_char()
                    self.value += self.char
                    if self.value in Lexer.special_symbols:
                        self.category = Lexer.special_symbols[self.value]
                        if not (self.category == Lexer.INPUT or self.category == Lexer.OUTPUT):
                            self.value = None
                        self.next_char()
                    else:
                        self.category = Lexer.ERROR
                else:
                    self.category = Lexer.ERROR
                    self.value = self.char
                    self.next_char()
