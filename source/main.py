import sys

from source.semantic_analyzer import SemanticAnalyzer


def main():
    try:
        program_file = sys.argv[1]
    except IndexError:
        print('Need to specify file program name to compile')
        return
    try:
        with open(program_file, 'r') as file:
            program_text = file.read()
    except FileNotFoundError:
        print("No such file: '{}'".format(program_file))
        return

    ast = SemanticAnalyzer(program_text).analyze()
    # print(ast)

if __name__ == '__main__':
    main()
