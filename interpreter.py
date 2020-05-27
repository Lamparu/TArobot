import sys
import copy
from YACC import ParserClass
from FLEX import data1
from SyntaxTree import node
from errors import *
# from errors import Error_handler
# from errors import UnexpectedError
# from errors import StartPointError
# from errors import IndexError
# from errors import RedeclarationError
# from errors import ElementDeclarationError
# from errors import ConverseError
# from errors import UndeclaredVariableError
# from errors import ArrayDeclarationError
# from errors import NotArrayError
# from errors import UndeclaredFunctionError
# from errors import CallWorkError


class variable:
    def __init__(self, v_type, v_name, v_value=None):
        if v_type == 'short int':
            v_type = 'short'
        self.type = v_type
        self.name = v_name
        if v_value is None:
            self.value = 0
        else:
            if self.type == 'bool':
                self.value = v_value
            elif self.type == 'short' and isinstance(v_value, str):
                if v_value[0] == 's':
                    self.value = int(v_value[1:])
                else: # if var = -s1
                    v_value = v_value[0] + v_value[2:]
                    self.value = int(v_value)
            else:
                self.value = int(v_value)

    def __repr__(self):
        return f'{self.type} {self.name} = {self.value}'


class arr_variable:
    def __init__(self, v_type, v_name, v_scope, v_array=None):
        if v_type == 'short int':
            v_type = 'short'
        self.type = v_type
        self.name = v_name
        self.scope = v_scope
        if v_array is None:
            self.array = []
            nuls = 0
            for i in list(v_scope.values()):
                nuls += i
            for j in range(nuls):
                self.array.append(0)
        else:
            self.array = v_array

    def __repr__(self):
        scopes = list(self.scope.values())
        return f'{self.type} {self.name}{scopes} = {self.array}'


"""  SIZES:
    sizeof(int) = 8     
    sizeof(short) = 2       -128 <= short <= 127
    sizeof(bool) = 1 
"""


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

    def sint_to_bool(self, var):
        if var.value > 0:
            return variable('bool', '', 'true')
        elif var.value < 0:
            return variable('bool', '', 'false')
        else:
            return variable('bool', '', 'undefined')

    def int_to_short(self, var):
        if var.value > 127 or var.value < -128:
            raise ConverseError
        return variable('short', '', var.value)

    def short_to_int(self, var):
        if isinstance(var.value, int):
            return variable('int', '', var.value)
        else:
            return variable('int', '', var.value[1:])

    def bool_to_int(self, var):
        if var.value == 'true':
            return variable('int', '', 1)
        elif var.value == 'false':
            return variable('int', '', -1)
        else:
            return variable('int', '', 0)

    def bool_to_short(self, var):
        if var.value == 'true':
            return variable('short', '', 1)
        elif var.value == 'false':
            return variable('short', '', -1)
        else:
            return variable('short', '', 0)


class interpreter:
    def __init__(self, program=None, robot=None):
        self.parser = ParserClass()
        self.converse = TypeConverser()
        self.error = Error_handler()
        self.scope = 0
        self.symbol_table = [dict()]
        self.er_types = {
            'UnexpectedError': 0,
            'StartPointError': 1,
            'IndexError': 2,
            'RedeclarationError': 3,
            'ElementDeclarationError': 4,
            'ConverseError': 5,
            'UndeclaredVariableError': 6,
            'ArrayDeclarationError': 7,
            'NotArrayError': 8,
            'UndeclaredFunctionError': 9,
            'CallWorkError': 10,
            'WrongParameterError': 11,
            'RobotError': 12
        }
        self.tree = None
        self.funcs = None
        self.correct = None
        self.program = program
        self.robot = robot
        self.exit = False

    def interpret(self):
        self.tree, self.funcs, self.correct = self.parser.parse(self.program)
        if self.correct:
            if 'work' not in self.funcs.keys():
                self.error.call(self.er_types['StartPointError'])
                return
            print('Program tree: \n')
            self.tree.print()
            print('\n')
            try:
                self.interp_node(self.funcs['work'].child['body'])
                return True
            except RecursionError:
                sys.stderr.write(f'RecursionError: function calls itself too many times\n')
                sys.stderr.write("========= Program has finished with fatal error =========\n")
                return False
        else:
            sys.stderr.write(f'Incorrect input file\n')

    def interp_node(self, node):  # TODO : EOS, NL
        if node is None:
            return
        elif node.type == 'error':
            self.error.call(self.er_types['UnexpectedError'], node)
        elif node.type == 'program':
            self.interp_node(node.child)
        elif node.type == 'group_stat':
            self.interp_node(node.child[1])
        elif node.type == 'statement list':
            self.interp_node(node.child[0])
            self.interp_node(node.child[1])
        # statement
        elif node.type == 'declaration':
            decl_type = node.child[0]
            decl_child = node.child[1]
            if decl_child.type == 'var_list':
                for child in decl_child.child:
                    try:
                        self.declaration(child, decl_type)
                    except RedeclarationError:
                        self.error.call(self.er_types['RedeclarationError'], node)
                    except IndexError:
                        self.error.call(self.er_types['IndexError'], node)
                    except ConverseError:
                        self.error.call(self.er_types['ConverseError'], node)
            else:
                try:
                    self.declaration(decl_type, decl_child)
                except RedeclarationError:
                    self.error.call(self.er_types['RedeclarationError'], node)
                except IndexError:
                    self.error.call(self.er_types['IndexError'], node)
                except ConverseError:
                    self.error.call(self.er_types['ConverseError'], node)

        elif node.type == 'assignment':
            self.assign_variable(node)
        # elif node.type == 'assignment array':
        #     self.assign_arr_variable(node)

        elif node.type == 'variable':
            return self._variable(node)
        elif node.type == 'arr variable':
            return self._arr_variable(node)
        elif node.type == 'digit':
            if node.value[0] == 's':
                return variable('short', '', node.value)
            else:
                return variable('int', '', node.value)
        elif node.type == 'bool':
            return variable('bool', '', node.value)
        elif node.type == 'EOS' or node.type == 'bracket':
            return node.value
        elif node.type == 'sizeof':
            return variable('int', '', self._sizeof(node))
        # elif node.type == 'index':
        #     indexes = []
        #     try:
        #         self._index(node, indexes)
        #     except IndexError:
        #         self.error.call(self.er_types['IndexError'], node)
        #     return indexes
        elif node.type == 'calculation':
            try:
                return self._calculation(node)
            except ConverseError:
                self.error.call(self.er_types['ConverseError'], node)
        elif node.type == 'expression':
            return self.interp_node(node.child[1])
        elif node.type == 'index':
            if isinstance(node.child, list):
                ind = []
                for ch in node.child:
                    ind.append(self.interp_node(ch))
                return ind
            else:
                return self.interp_node(node.ch)

        elif node.type == 'if_then':
            try:
                self.func_if_then(node)
            except ConverseError:
                self.error.call(self.er_types['ConverseError'], node)
            except IndexError:
                self.error.call(self.er_types['IndexError'], node)
        elif node.type == 'if_th_el':
            try:
                self.func_if_th_el(node)
            except ConverseError:
                self.error.call(self.er_types['ConverseError'], node)
            except IndexError:
                self.error.call(self.er_types['IndexError'], node)
        elif node.type == 'do_while':
            try:
                self.func_while(node)
            except ConverseError:
                self.error.call(self.er_types['ConverseError'], node)
            except IndexError:
                self.error.call(self.er_types['IndexError'], node)

        elif node.type == 'function':
            pass
        elif node.type == 'param':
            return self.combine_param(node)
        elif node.type == 'call_func':
            try:
                return self.call_function(node)
            except RecursionError:
                raise RecursionError from None

        elif node.type == 'command':
            if self.robot is None:
                self.error.call(self.er_types['RobotError'], node)
                self.correct = False
                return 0
            if node.value == 'lms':
                return variable('int', 'lms', self.robot.lms())
            else:
                self.robot.move(node.value)
                if self.robot.exit():
                    self.exit = True
                    return 1
        else:
            print('Not all nodes checked')



    # CALCULATION
    def _calculation(self, node):
        first_term = copy.deepcopy(self.interp_node(node.child[0]))
        second_term = copy.deepcopy(self.interp_node(node.child[1]))
        if isinstance(first_term, arr_variable) or isinstance(second_term, arr_variable):
            raise ConverseError
        if node.value == 'add':
            return self._add(first_term, second_term)
        if node.value == 'sub':
            return self._sub(first_term, second_term)
        if node.value == 'and':
            return self._and(first_term, second_term)
        if node.value == 'or':
            return self._or(first_term, second_term)
        if node.value == 'not or':
            return self._not_or(first_term, second_term)
        if node.value == 'not and':
            return self._not_and(first_term, second_term)
        elif node.value == 'first smaller' or node.value == 'second larger':
            return self._first_smaller(first_term, second_term)
        elif node.value == 'first larger' or node.value == 'second smaller':
            return self._first_larger(first_term, second_term)

    def _add(self, first, second):
        if first.type == 'bool':
            if second.type == 'short':
                self.converse.converse(first, 'short')
            else:
                self.converse.converse(first, 'int')
        if second.type == 'bool':
            if first.type == 'short':
                self.converse.converse(second, 'short')
            else:
                self.converse.converse(second, 'int')
        elif first.type == 'short' and second.type == 'int':
            self.converse.converse(first, 'int')
        elif first.type == 'int' and second.type == 'short':
            self.converse.converse(second, 'int')
        return variable('int', 'res', first.value + second.value)

    def _sub(self, first, second):
        if first.type == 'bool':
            if second.type == 'short':
                self.converse.converse(first, 'short')
            else:
                self.converse.converse(first, 'int')
        if second.type == 'bool':
            if first.type == 'short':
                self.converse.converse(second, 'short')
            else:
                self.converse.converse(second, 'int')
        elif first.type == 'short' and second.type == 'int':
            self.converse.converse(first, 'int')
        elif first.type == 'int' and second.type == 'short':
            self.converse.converse(second, 'int')
        return variable('int', 'res', first.value - second.value)

    def _first_smaller(self, first, second):
        if first.type == 'bool':
            first = self.converse.converse(first, 'int')
        if second.type == 'bool':
            second = self.converse.converse(second, 'int')
        if first.value > second.value:
            return variable('bool', 'res', 'false')
        elif first.value < second.value:
            return variable('bool', 'res', 'true')
        else:
            return variable('bool', 'res', 'undefined')

    def _first_larger(self, first, second):
        if first.type == 'bool':
            first = self.converse.converse(first, 'int')
        if second.type == 'bool':
            second = self.converse.converse(second, 'int')
        if first.value > second.value:
            return variable('bool', 'res', 'true')
        elif first.value < second.value:
            return variable('bool', 'res', 'false')
        else:
            return variable('bool', 'res', 'undefined')

    def _and(self, first, second):
        if first.type != 'bool':
            first = self.converse.converse(first, 'bool')
        if second.type != 'bool':
            second = self.converse.converse(second, 'bool')
        if first.value == 'true' and second.value == 'true':
            return variable('bool', 'res', 'true')
        elif first.value == 'true' and second.value == 'false':
            return variable('bool', 'res', 'false')
        elif first.value == 'true' and second.value == 'undefined':
            return variable('bool', 'res', 'undefined')
        elif first.value == 'false' and second.value == 'true':
            return variable('bool', 'res', 'false')
        elif first.value == 'false' and second.value == 'false':
            return variable('bool', 'res', 'false')
        elif first.value == 'false' and second.value == 'undefined':
            return variable('bool', 'res', 'undefined')
        elif first.value == 'undefined' and second.value == 'true':
            return variable('bool', 'res', 'undefined')
        elif first.value == 'undefined' and second.value == 'false':
            return variable('bool', 'res', 'false')
        elif first.value == 'undefined' and second.value == 'undefined':
            return variable('bool', 'res', 'undefined')

    def _or(self, first, second):
        if first.type != 'bool':
            first = self.converse.converse(first, 'bool')
        if second.type != 'bool':
            second = self.converse.converse(second, 'bool')
        if first.value == 'true' or second.value == 'true':
            return variable('bool', 'res', 'true')
        elif first.value == 'false' and second.value == 'false':
            return variable('bool', 'res', 'false')
        elif first.value == 'false' and second.value == 'undefined':
            return variable('bool', 'res', 'undefined')
        elif first.value == 'undefined' and second.value == 'false':
            return variable('bool', 'res', 'undefined')
        elif first.value == 'undefined' and second.value == 'undefined':
            return variable('bool', 'res', 'undefined')

    def _not_or(self, first, second):
        var = self._or(first, second)
        if var.value == 'true':
            var.value = 'false'
        elif var.value == 'false':
            var.value = 'true'
        return var

    def _not_and(self, first, second):
        var = self._and(first, second)
        if var.value == 'true':
            var.value = 'false'
        elif var.value == 'false':
            var.value = 'true'
        return var

    # def _index(self, node, indexes):
    #     if node.child is None:
    #         return indexes.append(node.value)
    #     else:
    #         return self._index(node.child, indexes)

    def _variable(self, node):
        var = node.value
        if var in self.symbol_table[self.scope].keys():
            return self.symbol_table[self.scope][var]
        else:
            raise UndeclaredVariableError

    def _arr_variable(self, node):
        if node.value not in self.symbol_table[self.scope].keys():
            raise UndeclaredVariableError
        var = self.symbol_table[self.scope][node.value]
        if isinstance(var, variable):
            raise NotArrayError
        i = self.get_el_index(node)
        # val = var.array[i]
        # return self.symbol_table[self.scope][node.value].array[i]
        type_var = var.type
        new_var = variable(type_var, node.value+str(i), self.symbol_table[self.scope][node.value].array[i])
        return new_var

    def get_el_index(self, var):
        ind = []
        ind = self.get_var_indexes(var, ind)
        if len(ind) == 1:
            return ind[0]
        var = self.symbol_table[self.scope][var.value]
        if len(list(var.scope.values())) != len(ind):
            raise IndexError
        for i in range(len(ind)):
            if ind[i] > var.scope[i] - 1 or ind[i] < 0:
                raise IndexError
        ind.reverse()
        scp = list(var.scope.values())
        scp.reverse()
        res = ind[0]
        sc = 1
        i = 1
        while i < len(ind):
            sc *= scp[i]
            res += ind[i] * sc
            i += 1
        return res

    def get_var_indexes(self, node, ind):
        if isinstance(node.child, list) and len(node.child) > 0:
            index = self.interp_node(node.child[0])
            if isinstance(index, arr_variable):
                raise IndexError
            index = copy.deepcopy(self.converse.converse(index, 'int'))
            if index.value < 0:
                raise IndexError
            ind.append(index.value)
            ind = self.get_var_indexes(node.child[1], ind)
        elif node.type != 'index' and node.type != 'arr variable':
            index = self.interp_node(node)
            if isinstance(index, arr_variable):
                raise IndexError
            index = copy.deepcopy(self.converse.converse(index, 'int'))
            if index.value < 0:
                raise IndexError
            ind.append(index.value)
        else:
            ind = self.get_var_indexes(node.child, ind)
        return ind

    def _sizeof(self, node):
        if node.child.type == 'type':
            tip = node.child.value
            return self.sizeof_type(tip)
        else:
            var = self.interp_node(node.child)
            if isinstance(var, arr_variable):
                raise WrongParameterError
            return self.sizeof_type(var.type)

    def sizeof_type(self, type):
        if type == 'short' or type == 'short int':
            return 2
        elif type == 'int':
            return 8
        else:
            return 1

    def declaration(self, type, node):
        if type.type == 'arr':
            if node.type == 'variable':
                raise ArrayDeclarationError
            arr_scope = self._arr_scope(type, 1)  # counting vector of
            arr_type = self._arr_type(type)
            if node.type == 'arr variable':
                if node.value in self.symbol_table[self.scope].keys() or node.value in self.funcs:
                    raise RedeclarationError
                index_scope = self._index_scope(node.child, 1)
                if index_scope != arr_scope:
                    raise ArrayDeclarationError
                arr_indexes = {}
                arr_indexes = self.get_indexes(node.child, arr_indexes, 0)
                var = arr_variable(arr_type, node.value, arr_indexes)
                self.symbol_table[self.scope][node.value] = var
            elif node.type == 'var_list':
                for ch in node.child:
                    self.declaration(type, ch)
            elif node.type == 'assignment':
                raise ArrayDeclarationError
            elif node.type == 'assignment array':
                var_ch = node.child[0]
                expr_ch = node.child[1]
                arr_name = var_ch.value
                if arr_name in self.symbol_table[self.scope].keys() or node.value in self.funcs:
                    raise RedeclarationError
                if var_ch.type == 'arr variable':
                    index_scope = self._index_scope(var_ch.child, 1)
                    if index_scope != arr_scope:
                        raise ArrayDeclarationError
                    arr_indexes = {}
                    arr_indexes = self.get_indexes(var_ch.child, arr_indexes, 0)
                    arr_values = self.get_arr_values(expr_ch, arr_type)
                    amount_items = self.count_items(arr_indexes)
                    if amount_items != len(arr_values):
                        raise ArrayDeclarationError
                    # TODO: to check indexes and arrays
                    var = arr_variable(arr_type, arr_name, arr_indexes, arr_values)
                    self.symbol_table[self.scope][arr_name] = var
                elif var_ch.type == 'variable':
                    arr_indexes = {}
                    arr_values = self.get_arr_values(expr_ch, arr_type, arr_indexes)
                    var = arr_variable(arr_type, arr_name, arr_indexes, arr_values)
                    self.symbol_table[self.scope][arr_name] = var
                    # TODO: to check scope of vector of and values

        else:  # if type.type == 'type'
            if node.type == 'variable':
                if node.value in self.symbol_table[self.scope].keys() or node.value in self.funcs:
                    raise RedeclarationError
                else:
                    self.symbol_table[self.scope][node.value] = variable(type.value, node.value)
            elif node.type == 'arr variable':
                raise ElementDeclarationError
            elif node.type == 'var_list':
                for ch in node.child:
                    self.declaration(type, ch)
            elif node.type == 'assignment array':
                raise ArrayDeclarationError
            else:  # if node.type == 'assignment'
                var = node.child[0].value
                if var in self.symbol_table[self.scope].keys() or node.value in self.funcs:
                    raise RedeclarationError
                if node.child[0].type != 'arr variable':
                    expr = self.interp_node(node.child[1])
                    expr = self.converse.converse(expr, type.value)
                    self.symbol_table[self.scope][var] = variable(type.value, var, expr.value)
                else:
                    raise ElementDeclarationError

    def _arr_scope(self, node, i):
        if node.child.type == 'type':
            return i
        else:
            return self._arr_scope(node.child, i + 1)

    def _index_scope(self, node, i):
        if isinstance(node.child, list):
            return self._index_scope(node.child[1], i + 1)
        else:
            return i

    def _arr_type(self, node):
        if node.type == 'type':
            return node.value
        else:
            return self._arr_type(node.child)

    def get_indexes(self, node, indexes, layer):
        if isinstance(node.child, list):
            var = self.interp_node(node.child[0])
            if isinstance(var, arr_variable):
                raise IndexError
            var = copy.deepcopy(self.converse.converse(var, 'int'))
            if var.value < 0:
                raise IndexError
            indexes[layer] = var.value
            return self.get_indexes(node.child[1], indexes, layer + 1)
        else:
            var = self.interp_node(node.child)
            if isinstance(var, arr_variable):
                raise IndexError
            var = copy.deepcopy(self.converse.converse(var, 'int'))
            if var.value < 0:
                raise IndexError
            indexes[layer] = var.value
            return indexes

    def get_arr_values(self, node, type, indexes=None):
        arr = []
        if node.type == 'array item':
            self.get_arr_const(node, type, arr)
            if indexes is not None:
                indexes[0] = len(arr)
        elif node.type == 'array':
            arr = self.get_arr_next(node, type, arr)
        else:
            arr.append(self.get_const(node, type))
            if indexes:
                indexes[0] = 1
        return arr

    def get_arr_next(self, node, type, arr):
        if isinstance(node.child, list):
            arr = self.get_arr_next(node.child[0], type, arr)
            if node.child[1].type == 'array':
                arr_new = self.get_arr_next(node.child[1], type, arr)
                for i in arr_new:
                    arr.append(i)
            else:
                self.get_arr_const(node.child[1], type, arr)
            return arr
        elif node.child.type == 'array':
            arr_n = self.get_arr_next(node.child, type, arr)
            for i in arr_n:
                arr.append(i)
            return arr
        else:
            arr_n = []
            self.get_arr_const(node.child, type, arr_n)
            return arr_n

    def get_arr_const(self, node, type, arr):
        if node.type == 'array item':
            arr.append(self.get_const(node.child[0], type))
            return self.get_arr_const(node.child[1], type, arr)
        else:
            arr.append(self.get_const(node, type))
            return arr

    def get_const(self, node, type):
        if node.type == 'bool':
            if type != 'bool':
                raise ArrayDeclarationError
            return node.value
        elif node.type == 'digit':
            if node.value[0] == 's' and type == 'int':
                raise ArrayDeclarationError
            return node.value
        elif node.type == 'sizeof':
            if type == 'bool':
                raise ArrayDeclarationError
            return self._sizeof(node)

    def count_items(self, ind):
        sum = 1
        for i in list(ind.values()):
            sum = sum * i
        return sum

    def assign_variable(self, node):
        var = node.child[0]
        if var.type == 'variable':
            if var.value not in self.symbol_table[self.scope].keys():
                self.error.call(self.er_types['UdeclaredVariableError'], node)
                raise UndeclaredVariableError
            expr = self.interp_node(node.child[1])
            variab = self.symbol_table[self.scope][var.value]
            if expr.type != variab.type:
                expr = self.converse.converse(expr, variab.type)
            if isinstance(variab, arr_variable) and isinstance(expr, arr_variable):
                self.symbol_table[self.scope][var.value].array = expr.array
            else:
                self.symbol_table[self.scope][var.value].value = expr.value
        elif var.type == 'arr variable':
            if var.value not in self.symbol_table[self.scope].keys():
                self.error.call(self.er_types['UndeclaredVariableError'], node)
                raise UndeclaredVariableError
            expr = self.interp_node(node.child[1])
            var_class = self.symbol_table[self.scope][var.value]
            if expr.type != var_class.type:
                expr = self.converse.converse(expr, var_class.type)
            ind = self.get_el_index(var)
            self.symbol_table[self.scope][var_class.name].array[ind] = str(expr.value)

    def func_if_then(self, node):
        condition = self.interp_node(node.child['condition'])
        condition = self.converse.converse(condition, 'bool').value
        if condition == 'true':
            self.interp_node(node.child['body'])

    def func_if_th_el(self, node):
        condition = self.interp_node(node.child['condition'])
        condition = self.converse.converse(condition, 'bool').value
        if condition == 'true':
            self.interp_node(node.child['body_1'])
        else:
            self.interp_node(node.child['body_2'])

    def func_while(self, node):
        try:
            while self.converse.converse(self.interp_node(node.child['condition']), 'bool').value == 'true':
                self.interp_node(node.child['body'])
        except ConverseError:
            self.error.call(self.er_types['ConverseError'], node)
        except IndexError:
            self.error.call(self.er_types['IndexError'], node)
        except UndeclaredVariableError:
            self.error.call(self.er_types['UndeclaredVariableError'], node)
        except RedeclarationError:
            self.error.call(self.er_types['RedeclarationError'], node)
        except ElementDeclarationError:
            self.error.call(self.er_types['ElementDeclarationError'], node)
        except NotArrayError:
            self.error.call(self.er_types['NotArrayError'], node)

    def call_function(self, node):
        name = node.value
        if self.scope > 100:
            self.scope = -1
            raise RecursionError
        if name not in self.funcs.keys():
            raise UndeclaredFunctionError
        if name == 'work':
            raise CallWorkError
        param = node.child
        input_param = []
        change_value = []
        try:
            while param is not None:
                if param.type == 'func_param':
                    if param.value == 'none':
                        input_param = []
                    else:
                        # if param.child[1].type == 'arr variable':
                        #     if param.child[1].value not in self.symbol_table[self.scope].keys():
                        #         raise UndeclaredVariableError
                        #     var = self.symbol_table[self.scope][param.child[1].value]
                        #     if isinstance(var, variable):
                        #         raise NotArrayError
                        #     index = self.get_el_index(param.child[1])
                        #     val = var.array[index]
                        #     arr_var = variable(self.symbol_table[self.scope][param.child[1].value].type,
                        #                        param.child[1].value+str(index), val)
                        #     input_param.append(arr_var)
                        # else:
                        #     input_param.append(self.interp_node(param.child[1]))
                        # p = self.interp_node(param.child[1])
                        # input_param.append(p)
                        input_param.append(self.interp_node(param.child[1]))
                        if param.child[1].type == 'arr variable':
                            change_value.append(len(input_param)-1)
                        param = param.child[0]
                else:
                    # if param.type == 'arr variable':
                    #     if param.value not in self.symbol_table[self.scope].keys():
                    #         raise UndeclaredVariableError
                    #     var = self.symbol_table[self.scope][param.value]
                    #     if isinstance(var, variable):
                    #         raise NotArrayError
                    #     index = self.get_el_index(param)
                    #     val = var.array[index]
                    #     arr_var = variable(self.symbol_table[self.scope][param.value].type,
                    #                        param.value + str(index), val)
                    #     input_param.append(arr_var)
                    # else:
                    #     input_param.append(self.interp_node(param))
                    # p = self.interp_node(param)
                    # input_param.append(p)
                    input_param.append(self.interp_node(param))
                    if param.type == 'arr variable':
                        change_value.append(len(input_param)-1)
                    break
            input_param.reverse()
            for i in range(len(change_value)):
                change_value[i] = -change_value[i] - 1
        except NotArrayError:
            self.error.call(self.er_types['NotArrayError'], node)
        except IndexError:
            self.error.call(self.er_types['IndexError'], node)
        self.scope += 1
        self.symbol_table.append(dict())
        func_param = []
        node_param = self.funcs[name].child['parameters']
        func_param = self.get_parameter(node_param)
        if len(func_param) != len(input_param):
            raise WrongParameterError
        for i in range(len(input_param)):
            self.set_param(input_param[i], func_param[i])
        for par in func_param:
            self.symbol_table[self.scope][par.name] = par
        self.interp_node(self.funcs[name].child['body'])
        result = copy.deepcopy(self.interp_node(self.funcs[name].child['return']))
        self.symbol_table.pop()
        self.scope -= 1
        for i in range(len(input_param)):
            name = input_param[i].name
            input_param[i] = copy.deepcopy(func_param[i])
            input_param[i].name = name
            # self.symbol_table[self.scope][input_param[i].name] = copy.deepcopy(func_param[i])
            # self.symbol_table[self.scope][input_param[i].name].name = input_param[i].name
        for p in change_value:
            par = input_param[p]
            arr_type = self.symbol_table[self.scope][par.name[:-1]].type
            if par.type != arr_type:
                par = self.converse.converse(par, arr_type)
            self.symbol_table[self.scope][par.name[:-1]].array[int(par.name[-1])] = str(par.value)
            input_param[p] = None
            func_param[p] = None
            for var in input_param:
                if var is not None:
                    self.symbol_table[self.scope][var.name] = var
        return result


    def get_parameter(self, node):
        if node.type == 'param_none':
            return []
        param = []
        while isinstance(node.child, list):
            if node.type == 'param arr':
                param.append(self.interp_node(node.child[0]))
                param.append(self.interp_node(node.child[1]))
            elif node.type == 'param':
                param.append(self.combine_param(node))
            if len(node.child) == 0 or node.child[0].type == 'param':
                break
            node = node.child[0]
        #param.reverse()
        return param

    def combine_param(self, node):
        type_node = node.child[0]
        ch_node = node.child[1]
        if ch_node.type == 'arr variable':
            raise WrongParameterError
        if type_node.type == 'type':
            type = type_node.value
            return variable(type, ch_node.value)

        else: # type_node.type == 'arr':
            arr_scope = self._arr_scope(type_node, 1)
            arr_type = self._arr_type(type_node)
            scope = {}
            for i in range(arr_scope):
                scope[i] = 0
            return arr_variable(arr_type, ch_node.value, scope)
            # else:
            #     arr_indexes = {}
            #     arr_indexes = self.get_indexes(ch_node.child, arr_indexes, 0)
            #     if len(arr_indexes.keys()) != arr_scope:
            #         raise ArrayDeclarationError
            #     return arr_variable(arr_type, ch_node.value, arr_indexes)

    def set_param(self, input, func):
        #input = copy.deepcopy(self.converse.converse(input, func.type))
        if input.type == 'int' and input.name == "" and func.type == 'short':
            input = self.converse.converse(input, 'short')
        if input.type != func.type:
            raise WrongParameterError
        if isinstance(input, arr_variable) and isinstance(func, arr_variable):
            k = 0
            for i in input.scope.values():
                func.scope[k] = i
                k += 1
            func.array = input.array
        elif isinstance(input, variable) and isinstance(func, variable):
            func.value = input.value
        else:
            raise WrongParameterError

    def set_param1(self, input, func):
        #input = copy.deepcopy(self.converse.converse(input, func.type))
        if input.type == 'int' and input.name == "" and func.type == 'short':
            input = self.converse.converse(input, 'short')
        if input.type != func.type:
            raise WrongParameterError
        if isinstance(input, arr_variable) and isinstance(func, arr_variable):
            func = input
        elif isinstance(input, variable) and isinstance(func, variable):
            func = input
        else:
            raise WrongParameterError



if __name__ == '__main__':
    # f = open('algosort.txt')
    f = open('factorial.txt')
    data = f.read().lower()
    f.close()
    prog = data
    i = interpreter(program=prog)
    res = i.interpret()
    if res:
        print(i.symbol_table)
    else:
        print('===SOMETHING WRONG===')
    if i.exit:
        print('Robot found exit!')
    else:
        print('Robot can\'t find exit')
