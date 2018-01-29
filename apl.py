#!/usr/bin/python3

import sys
import ply.lex as lex
import ply.yacc as yacc

pointer_id_list = []
static_id_list = []
no_assignments = 0

reserved_keywords = {
    'void': 'VOID',
    'main': 'MAIN',
    'int': 'INT',
}

tokens = [
    'ID',
    'L_PAREN', 'R_PAREN',
    'L_CURLY', 'R_CURLY',
    'SEMICOLON',
    'COMMA',
    'EQUALS',
    'AMPERSAND',
    'ASTERISK',
    'NUMBER',
]

tokens = tokens + list(reserved_keywords.values())

t_ignore = ' \t\n'

t_ASTERISK = r'\*'
t_AMPERSAND = r'&'
t_SEMICOLON = r';'
t_COMMA = r','
t_EQUALS = r'='
t_L_CURLY = r'{'
t_R_CURLY = r'}'
t_L_PAREN = r'\('
t_R_PAREN = r'\)'


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved_keywords.get(t.value, 'ID')
    return t


def t_NUMBER(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        print("Integer value too large %d", t.value)
        t.value = 0
    return t


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Parsing rules
precedence = (
    ('right', 'EQUALS'),
    ('right', 'AMPERSAND', 'ASTERISK'),
)


def p_code(p):
    """code : VOID MAIN L_PAREN R_PAREN L_CURLY body R_CURLY"""
    pass


def p_body(p):
    """
    body : statement SEMICOLON body
            | statement SEMICOLON
    """
    pass


def p_statement(p):
    """
    statement : INT dlist
                | alist
    """
    pass


def p_dlist(p):
    """
    dlist : declaration COMMA dlist
            | declaration
    """
    pass


def p_pointer_declaration(p):
    """
    declaration : ASTERISK ID
    """
    pointer_id_list.append(p[2])


def p_static_declaration(p):
    """
    declaration : ID
    """
    static_id_list.append(p[1])


def p_alist(p):
    """
    alist : assignment COMMA alist
            | assignment
    """
    pass


def p_assignment_2(p):
    """assignment : ID EQUALS assignment
                | ASTERISK ID EQUALS assignment
    """
    global no_assignments
    no_assignments += 1
    pass


def p_assignment_1(p):
    """
    assignment :  ID EQUALS AMPERSAND ID
                | ASTERISK ID EQUALS NUMBER
                | ASTERISK ID EQUALS ASTERISK ID
                | ID EQUALS ID
                | ASTERISK ID EQUALS ID
    """
    global no_assignments
    no_assignments += 1
    pass


# def p_statement_expr(p):
#     """statement : expression"""
#     print(p[1])
#
#
# def p_expression_binop(p):
#     """
#     expression : expression PLUS expression
#                         | expression MINUS expression
#                         | expression TIMES expression
#                         | expression DIVIDE expression
#                         | expression EXP expression
#                         | expression PLUS_LIT expression
#                         | expression MINUS_LIT expression
#                         | expression TIMES_LIT expression
#                         | expression DIVIDE_LIT expression
#                         | expression EXP_LIT expression
#     """
#     if p[2] == '+' or p[2] == 'plus':
#         p[0] = p[1] + p[3]
#     elif p[2] == '-' or p[2] == 'minus':
#         p[0] = p[1] - p[3]
#     elif p[2] == '*' or p[2] == 'times':
#         p[0] = p[1] * p[3]
#     elif p[2] == '/' or p[2] == 'divide':
#         p[0] = p[1] / p[3]
#     elif p[2] == '**' or p[2] == 'power':
#         p[0] = p[1] ** p[3]
#
#
# def p_expression_uminus(p):
#     """expression : MINUS expression %prec UMINUS
#                                 | MINUS_LIT expression %prec UMINUS"""
#     p[0] = -p[2]
#
#
# def p_expression_group(p):
#     """expression : LPAREN expression RPAREN"""
#     p[0] = p[2]
#
#
# def p_expression_number(p):
#     """expression : NUMBER"""
#     p[0] = p[1]
#
#
# def p_expression_name(p):
#     """expression : ID"""
#     try:
#         p[0] = p[1]
#     except LookupError:
#         print("Undefined name '%s'" % p[1])
#         p[0] = 0


def p_error(p):
    if p:
        print("syntax error at {0}".format(p.value))
    else:
        print("syntax error at EOF")


def process(data):
    lex.lex()
    yacc.yacc()
    yacc.parse(data)
    print(len(static_id_list))
    print(len(pointer_id_list))
    print(no_assignments)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage :', sys.argv[0], 'source_file_path')
        exit(-1)
    source_code_file = open(sys.argv[1], 'r')
    source_code = ''
    for line in source_code_file:
        source_code += line
    # print(source_code)
    process(source_code)
