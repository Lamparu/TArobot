import ply.yacc as yacc
from FLEX import LexerClass
from SyntaxTree import node
from FLEX import data1
from ply.lex import LexError


class ParserClass:
    tokens = LexerClass.tokens

    def __init__(self):
        self.lexer = LexerClass()
        self.parser = yacc.yacc(module=self, optimize=1, debug=False, write_tables=False)
        self.flag = False

    def parse(self, s):
        try:
            res = self.parser.parse(s)
            return res
        except LexError:
            print('Illegal token ' + s)

    def p_program(self, p):
        """program : stat_list"""
        p[0] = node('program', ch=p[1], no=p.lineno(1))

    def p_stat_list(self, p):
        """stat_list : stat_list statement ENDSTR NL
                    | statement ENDSTR NL"""
        if len(p) == 4:
            p[2] = node('EOS', val=p[2])
            p[0] = node('statement list', ch=[p[1], p[2]], no=p.lineno(1))
        else:
            p[3] = node('EOS', val=p[3])
            p[0] = node('statement list', ch=[p[1], p[2], p[3]], no=p.lineno(2))

    def p_statement(self, p):
        """statement : declaration
                    | assignment
                    | sizeof"""
        p[0] = p[1]

    def p_type(self, p):
        """type : INT
                | SHORT INT
                | SHORT
                | BOOL"""
        if len(p) == 2:
            p[0] = node('type', val=p[1], ch=[], no=p.lineno(1))
        else:
            p[0] = node('type', val=p[1]+' '+p[2], ch=[], no=p.lineno(1))

    def p_type_vec(self, p):
        """type : vectorof"""
        p[0] = p[1]

    def p_vectorof(self, p):
        """vectorof : VECTOROF type
                    | VECTOROF vectorof"""
        p[0] = node('arr', val=str(p[1]), ch=p[2], no=p.lineno(1))

    def p_digit(self, p):
        """digit : INTLIT
                | SHORTLIT"""
        p[0] = node('digit', val=p[1], no=p.lineno(1))

    def p_bool(self, p):
        """bool : TRUE
                | FALSE
                | UNDEFINED"""
        p[0] = node('bool', val=p[1], no=p.lineno(1))

    def p_expr(self, p):
        """expr : variable
                | const
                | math_expr"""
        p[0] = p[1]
        #p[0] = node('expression', ch=p[1], no=p.lineno(1))

    def p_math_expr(self, p):
        """math_expr : expr ADD expr
                | expr SUB expr
                | expr FIRST SMALLER expr
                | expr SECOND LARGER expr
                | expr SECOND SMALLER expr
                | expr FIRST LARGER expr
                | expr OR expr
                | expr NOT OR expr
                | expr AND expr
                | expr NOT AND expr"""
        if len(p) == 4:
            p[0] = node('calculation', val=p[2], ch=[p[1], p[3]], no=p.lineno(1))
        else:
            p[0] = node('calculation', val=p[2]+' '+p[3], ch=[p[1], p[4]], no=p.lineno(1))

    def p_expr_br(self, p):
        """expr : OPBR expr CLBR"""
        p[1] = node('bracket', val=p[1], no=p.lineno(1))
        p[3] = node('bracket', val=p[3], no=p.lineno(3))
        p[0] = node('expression', ch=[p[1], p[2], p[3]], no=p.lineno(2))

    def p_const(self, p):
        """const : digit
                | bool
                | sizeof"""
        p[0] = p[1]

    def p_sizeof(self, p):
        """sizeof : SIZEOF OPBR type CLBR
                | SIZEOF OPBR STRLIT CLBR"""
        p[0] = node('sizeof', val=p[1], ch=p[3], no=p.lineno(1))

    def p_declaration(self, p):
        """declaration : type var_list"""
        p[0] = node('declaration', ch=[p[1], p[2]], no=p.lineno(2))

    def p_var_list(self, p):
        """var_list : variable
                    | assignment
                    | var_list COMMA var_list """
        if len(p) == 2:
            p[0] = p[1]
            #p[0] = node('vars', ch=p[1], no=p.lineno(1))
        else:
            p[0] = node('vars', ch=[p[1], p[3]], no=p.lineno(1))

    def p_assignment(self, p):
        """assignment : variable SET expr
                        | variable SET arr_start
                        | vec_var SET arr_start"""
        p[0] = node('assignment', val=p[2], ch=[p[1], p[3]], no=p.lineno(1))

    def p_vec_var(self, p):
        """vec_var : vectorof variable"""
        p[0] = node('arr', val=p[1], ch=p[2], no=p.lineno(1))

    # def p_arr_set(self, p):
    #     """arr_set : OPCUBR arr_start CLCUBR"""
    #     p[1] = node('bracket', val=p[1], no=p.lineno(1))
    #     p[3] = node('bracket', val=p[3], no=p.lineno(3))
    #     p[0] = node('array', ch=[p[1], p[2], p[3]], no=p.lineno(2))

    def p_arr_start(self, p):
        """arr_start : OPCUBR arr_end arr_end CLCUBR
                    | OPCUBR const_arr CLCUBR"""
        if len(p) == 5:
            p[1] = node('bracket', val=p[1], no=p.lineno(1))
            p[4] = node('bracket', val=p[4], no=p.lineno(1))
            p[0] = node('array list', ch=[p[1], p[2], p[3], p[4]], no=p.lineno(1))
        elif len(p) == 4:
            p[1] = node('bracket', val=p[1], no=p.lineno(1))
            p[3] = node('bracket', val=p[3], no=p.lineno(1))
            p[0] = node('array list', ch=[p[1], p[2], p[3]], no=p.lineno(1))


    def p_arr_end(self, p):
        """arr_end : CLCUBR COMMA
                    | CLCUBR
                    | OPCUBR const_arr arr_end
                    | OPCUBR arr_end"""
        if len(p) == 2:
            p[0] = node('bracket', val=p[1], no=p.lineno(1))
        elif len(p) == 3:
            if p[2] != ',':
                p[0] = node('bracket', val=p[1], ch=p[2], no=p.lineno(1))
            else:
                p[0] = node('bracket', val=p[1], no=p.lineno(1))
        else:
            p[1] = node('bracket', val=p[1], no=p.lineno(1))
            p[0] = node('array list', ch=[p[1], p[2], p[3]], no=p.lineno(1))

    def p_const_arr(self, p):
        """const_arr : const
                    | const COMMA const_arr"""
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            p[0] = node('array', ch=[p[1], p[3]], no=p.lineno(1))

    def p_variable(self, p):
        """variable : STRLIT
                    | STRLIT index"""
        if len(p) == 2:
            p[0] = node('variable', val=p[1], no=p.lineno(1))
        else:
            p[0] = node('arr variable', val=p[1], ch=p[2], no=p.lineno(1))

    def p_index(self, p):
        """index : OPSQBR digit CLSQBR
                | OPSQBR digit CLSQBR index"""
        if len(p) == 4:
            p[0] = node('index', val=p[2], no=p.lineno(2))
        else:
            p[0] = node('index', val=p[2], ch=p[4], no=p.lineno(2))

    def p_error(self, p):
        print("Syntax error in input!")



if __name__ == '__main__':
    parser = ParserClass()
    tree = parser.parser.parse(data1, debug=True)
    tree.print()
