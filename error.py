program_text = []


def init_program_text(prog_text):
    global program_text
    program_text = prog_text.split('\n')


def generate_error(error_type, error_message, line, column):
    print('{error_type} Error on {line}:{column}: {error_message}:'.format(
        error_type=error_type, error_message=error_message, line=line, column=column))
    raw_line = program_text[line - 1]
    print(raw_line)
    tabs = raw_line[:column].count('\t')
    caret_line = ' ' * (column - 1) + ' ' * 3 * tabs + '^'
    print(caret_line)
