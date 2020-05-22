import sys
import SyntaxTree


class Error_handler:
    def __init__(self):
        self.type = None
        self.node = None
        self.types = [
            'UnexpectedError',
            'StartPointError',
            'IndexError',
            'RedeclarationError',
            'ElementDeclarationError',
            'ConverseError',
            'UndeclaredVariableError'
        ]

    def call(self, err_type, node=None):
        self.type = err_type
        self.node = node
        sys.stderr.write(f'Error {self.types[int(err_type)]}: ')
        if self.type == 0:
            sys.stderr.write(f'Incorrect syntax at {self.node.children[0].lineno} line \n')
            return
        elif self.type == 1:
            sys.stderr.write(f'No WORK function in program\n')
        elif self.type == 2:
            sys.stderr.write(f'Index is wrong at line {self.node.value.lineno}\n')
        elif self.type == 3:
            sys.stderr.write(f'Redeclaration of a variable "{self.node.value.value}" at line {self.node.value.lineno}\n')
        elif self.type == 4:
            sys.stderr.write(f'Declared element of array at line {self.node.value.lineno}')
        elif self.type == 5:
            sys.stderr.write(f'Can\'t converse types at line {self.node.value.lineno}')
        elif self.type == 6:
            sys.stderr.write(f'Using undeclared variable "{self.node.value.value}" at line {self.node.value.lineno}')


class UnexpectedError(Exception):
    pass


class StartPointError(Exception):
    pass


class IndexError(Exception):
    pass


class RedeclarationError(Exception):
    pass


class ElementDeclarationError(Exception):
    pass


class ConverseError(Exception):
    pass


class UndeclaredVariableError(Exception):
    pass
