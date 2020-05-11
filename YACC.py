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
            print(f'Illegal token {s}\n')

    def p_type(self, p):
        """type : INT
                | SHORT INT
                | SHORT
                | BOOL"""
        if len(p) == 2:
            p[0] = node('type', val=p[1], ch=[], no=p.lineno(1), pos=p.lexpos(1))
        else:
            p[0] = node('type', val=p[1]+' '+p[2], ch=[], no=p.lineno(1), pos=p.lexpos(1))

    def p_vectorof(self, p):
        """vectorof : VECTOROF type
                    | VECTOROF vectorof"""
        p[0] = node('vector', val=p[1] + ' ' + p[2], ch=[], no=p.lineno(1), pos=p.lexpos(1))

    def p_digit(self, p):
        """digit : INTLIT
                | SHORTLIT"""
        p[0] = node('digit', val=p[1], no=p.lineno(1), pos=p.lexpos(1))

    def p_bool(self, p):
        """bool : TRUE
                | FALSE
                | UNDEFINED"""
        p[0] = node('bool', val=p[1], no=p.lineno(1), pos=p.lexpos(1))

    def p_expr_calc(self, p):
        """expr : expr ADD expr
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
            p[0] = node('calculation', val=p[2], ch=[p[1], p[3]], no=p.lineno(1), pos=p.lexpos(1))
        else:
            p[0] = node('calculation', val=p[2]+' '+p[3], ch=[p[1], p[4]], no=p.lineno(1), pos=p.lexpos(1))

    def p_expr_br(self, p):
        """expr : OPBR expr CLBR"""
        p[0] = node('expression', val=p[2], ch=[p[1], p[3]], no=p.lineno(1), pos=p.lexpos(1))

    def p_expr_type(self, p):
        """expr : digit
                | bool"""
        p[0] = p[1]

    def p_sizeof(self, p):
        """sizeof : SIZEOF OPBR type CLBR
                | SIZEOF OPBR STRLIT CLBR"""
        p[0] = node('sizeof', val=p[1], ch=p[3], no=p.lineno(1), pos=p.lexpos(1))

    def p_declaration_var(self, p):
        """declaration : type variable"""
        p[0] = node('type', val=p[1], ch=p[2], no=p.lineno(2), pos=p.lexpos(2))

    def p_variable(self, p):
        """variable : STRLIT
                | STRLIT COMMA variable"""
        if len(p) == 2:
            p[0] = node('variable', ch=p[1], no=p.lineno(1), pos=p.lexpos(1))
        else:
            p[0] = node('variable', ch=[p[1], p[3]], no=p.lineno(1), pos=p.lexpos(1))

    def p_variable_set(self, p):
        """variable : variable SET expr
                    | STRLIT SET expr"""
        p[0] = node('set', val=p[2], ch=p[1]+' '+p[3], no=p.lineno(1), pos=p.lexpos(1))





if __name__ == '__main__':
    parser = ParserClass()
    tree = parser.parse(data1)
    tree.print()
