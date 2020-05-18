import sys
from YACC import ParserClass
from SyntaxTree import node
from errors import Error_handler


class variable:
    def __init__(self, v_type, v_value):
        self.type = v_type
        if self.type == 'bool':
            self.value = v_value
        elif self.type == 'short' and not isinstance(v_value, int):  # TODO: сделать short int и short как одно
            self.value = int(v_value[1:])
        else:
            self.value = int(v_value)

    def __repr__(self):
        return f'{self.type} {self.value}'


class TypeConverser:
    def __init__(self):
        pass

    def converse(self, var, vartype):
        if vartype == var.type:
            return var
        elif vartype == 'bool':
            return self.sint_to_bool(var)
        elif vartype == 'int':
            if var.type == 'short':
                return self.short_to_int(var)
            elif var.type == 'bool':
                return self.bool_to_int(var)
        elif vartype == 'short':
            if var.type == 'int':
                return self.int_to_short(var)
            elif var.type == 'bool':
                return self.bool_to_short(var)
        # TODO : мб еще ошибок добавить

    def sint_to_bool(self, var):
        if var.value > 0:
            return variable('bool', 'true')
        elif var.value < 0:
            return variable('bool', 'false')
        else:
            return variable('bool', 'undefined')

    def int_to_short(self, var):
        return variable('short', var.value)

    def short_to_int(self, var):
        if isinstance(var.value, int):
            return variable('int', var.value)
        else:
            return variable('int', var.value[1:])

    def bool_to_int(self, var):
        if var.value == 'true':
            return variable('int', 1)
        elif var.value == 'false':
            return variable('int', -1)
        else:
            return variable('int', 0)

    def bool_to_short(self, var):
        if var.value == 'true':
            return variable('short', 1)
        elif var.value == 'false':
            return variable('short', -1)
        else:
            return variable('short', 0)


class interpreter:
    def __init__(self, code=None):
        self.parser = ParserClass()
        self.converse = TypeConverser()
        self.error = Error_handler()
        self.er_types = {
            'UnexpectedError': 0,
            'StartPointError': 1,
            'IndexError': 2,
            'RedeclarationError': 3
        }
        self.tree = None
        self.funcs = None
        self.correct = None
        self.code = code

    def interpret(self):
        self.tree, self.funcs, self.correct = self.parser.parse(self.code)
        if self.correct:
            if 'work' not in self.funcs.keys():
                self.error.call(self.er_types['StartPointError'])
                return
            print('Program tree: \n')
            self.tree.print()
            print('\n')
            try:
                self.interp_node(self.funcs['work'].children['body'])
                return True
            except RecursionError:
                sys.stderr.write(f'RecursionError: function calls itself too many times\n')
                sys.stderr.write("========= Program has finished with fatal error =========\n")
                return False
        else:
            sys.stderr.write(f'Incorrect input file\n')

    def interp_node(self, node):  # TODO : EOS, NL
        if node is None:
            return ''
        elif node.type == 'program':
            self.interp_node(node.children)
        elif node.type == 'statement list':
            self.interp_node(node.children[0])
            self.interp_node(node.children[1])
        #statement
        elif node.type == 'declaration':
            try:
                self.declare(node.value.value, node.child)
            except RedeclarationError:
                self.error.call(self.er_types['RedeclarationError'], node)
            except IndexError:
                self.error.call(self.er_types['IndexError'], node)




    def declare(self, type, child):

