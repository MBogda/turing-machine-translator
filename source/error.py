program_text = []

lexer_errors = False
parser_errors = False
semantic_errors = False


def get_lexer_errors():
    return lexer_errors


def get_parser_errors():
    return parser_errors


def get_semantic_errors():
    return semantic_errors


def init_program_text(prog_text):
    global program_text
    program_text = prog_text.split('\n')


def generate_error(error_type, error_message, line, column):
    if error_type == 'Lexer':
        lexer_errors = True
    elif error_type == 'Parser':
        parser_errors = True
    elif error_type == 'Semantic':
        semantic_errors = True

    print('{error_type} Error on {line}:{column}: {error_message}:'.format(
        error_type=error_type, error_message=error_message, line=line, column=column))
    raw_line = program_text[line - 1]
    print(' ' + raw_line.replace('\t', ' '))
    caret_line = ' ' * column + '^'
    print(caret_line)
