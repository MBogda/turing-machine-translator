class Lexer:
    # tokens
    (
        IDENTIFIER, INTEGER_LITERAL, SYMBOL_LITERAL, TAPE_LITERAL,
        TRUE, FALSE,
        LEFT_BRACE, RIGHT_BRACE, LEFT_BRACKET, RIGHT_BRACKET, LEFT_SQUARE_BRACKET, RIGHT_SQUARE_BRACKET,
        COLON,
        PLUS, LEFT_PLUS, RIGHT_PLUS, MINUS, MULTIPLY, DIVIDE, MODULO,
        MARKER_PLUS, MARKER_MINUS, MARKER_MULTIPLY, MARKER_DEVIDE, MARKER_MODULO,
        EQUAL, NOT_EQUAL, LESS, GREATER, LESS_OR_EQUAL, GREATER_OR_EQUAL,
        ASSIGNMENT, ASSIGNMENT_PLUS, ASSIGNMENT_LEFT_PLUS, ASSIGNMENT_RIGHT_PLUS,
        ASSIGNMENT_MINUS, ASSIGNMENT_MULTIPLY, ASSIGNMENT_DIVIDE, ASSIGNMENT_MODULO,
        AND, OR, NOT,
        IF, ELIF, ELSE, WHILE,
        INDENT, DEDENT,
        INPUT, OUTPUT,
        NEW_LINE, EOF, ERROR,
    ) = range(53)

    # tokens
    tokens = [
        'IDENTIFIER', 'INTEGER_LITERAL', 'SYMBOL_LITERAL', 'TAPE_LITERAL',
        'TRUE', 'FALSE',
        'LEFT_BRACE', 'RIGHT_BRACE', 'LEFT_BRACKET', 'RIGHT_BRACKET', 'LEFT_SQUARE_BRACKET', 'RIGHT_SQUARE_BRACKET',
        'COLON',
        'PLUS', 'LEFT_PLUS', 'RIGHT_PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'MODULO',
        'MARKER_PLUS', 'MARKER_MINUS', 'MARKER_MULTIPLY', 'MARKER_DEVIDE', 'MARKER_MODULO',
        'EQUAL', 'NOT_EQUAL', 'LESS', 'GREATER', 'LESS_OR_EQUAL', 'GREATER_OR_EQUAL',
        'ASSIGNMENT', 'ASSIGNMENT_PLUS', 'ASSIGNMENT_LEFT_PLUS', 'ASSIGNMENT_RIGHT_PLUS',
        'ASSIGNMENT_MINUS', 'ASSIGNMENT_MULTIPLY', 'ASSIGNMENT_DIVIDE', 'ASSIGNMENT_MODULO',
        'AND', 'OR', 'NOT',
        'IF', 'ELIF', 'ELSE', 'WHILE',
        'INDENT', 'DEDENT',
        'INPUT', 'OUTPUT',
        'NEW_LINE', 'EOF', 'ERROR',
    ]

    # special symbols
    special_symbols = {
        '{': LEFT_BRACE, '}': RIGHT_BRACE,
        '(': LEFT_BRACKET, ')': RIGHT_BRACKET,
        '[': LEFT_SQUARE_BRACKET, ']': RIGHT_SQUARE_BRACKET,
        ':': COLON,
        '+': PLUS, '<+': LEFT_PLUS, '+>': RIGHT_PLUS, '-': MINUS, '*': MULTIPLY, '/': DIVIDE, '%': MODULO,
        '^+': MARKER_PLUS, '^-': MARKER_MINUS, '^*': MARKER_MULTIPLY, '^/': MARKER_DEVIDE, '^%': MARKER_MODULO,
        '==': EQUAL, '!=': NOT_EQUAL, '<': LESS, '>': GREATER, '<=': LESS_OR_EQUAL, '>=': GREATER_OR_EQUAL,
        '=': ASSIGNMENT, '+=': ASSIGNMENT_PLUS, '<+=': ASSIGNMENT_LEFT_PLUS, '+>=': ASSIGNMENT_RIGHT_PLUS,
        '=-': ASSIGNMENT_MINUS, '=*': ASSIGNMENT_MULTIPLY, '=/': ASSIGNMENT_DIVIDE, '=%': ASSIGNMENT_MODULO,
        '>b': INPUT, '>i': INPUT, ">'": INPUT, '>"': INPUT,
        '<b': OUTPUT, '<i': OUTPUT, "<'": OUTPUT, '<"': OUTPUT,
    }

    special_symbol_characters = {char for symbol in special_symbols for char in symbol}

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
            self.char = None
        else:
            self.char = self.text[self.index]
            self.index += 1

    def next_token(self):
        self.value = None
        self.category = None
        while self.category is None:
            if self.char is None:
                self.category = Lexer.EOF
            elif self.char.isspace():
                self.next_char()
            elif self.char.isdigit():
                self.value = 0
                while self.char.isdigit():
                    self.value *= 10
                    self.value += int(self.char)
                    self.next_char()
                self.category = Lexer.INTEGER_LITERAL
            elif self.char.isalpha() or self.char == '_':
                self.value = ''
                while self.char.isalpha() or self.char == '_' or self.char.isdigit():
                    self.value += self.char
                    self.next_char()
                if self.value in self.keywords:
                    self.category = self.keywords[self.value]
                    self.value = None
                else:
                    self.category = Lexer.IDENTIFIER
            else:
                self.value = ''
                while not (self.char is None or self.char.isspace() or self.char.isdigit() or self.char.isalpha()
                           or self.char == '_'):
                    self.value += self.char
                    self.next_char()
                if self.value in Lexer.special_symbols:
                    self.category = Lexer.special_symbols[self.value]
                    self.value = None
                else:
                    self.category = Lexer.ERROR
