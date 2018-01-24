#!/usr/bin/python3

import sys
import ply.lex as lex
import ply.yacc as yacc

reserved_keywords = {
    'main': 'MAIN',
    'void': 'VOID',
    'int': 'INT',
}

tokens = [
    'STATIC_ID',
    'POINTER_ID',
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


def t_STATIC_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved_keywords.get(t.value, 'STATIC_ID')
    return t


def t_POINTER_ID(t):
    r'\*[a-zA-Z_][a-zA-Z0-9_]*'
    t.value = t.value[1:]
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
    ('right', 'ASTERISK', 'AMPERSAND'),
)


def p_statement_assign(p):
    """statement : NAME EQUALS expression"""
    p[1] = p[3]


def p_statement_expr(p):
    """statement : expression"""
    print(p[1])


def p_expression_binop(p):
    """
    expression : expression PLUS expression
                        | expression MINUS expression
                        | expression TIMES expression
                        | expression DIVIDE expression
                        | expression EXP expression
                        | expression PLUS_LIT expression
                        | expression MINUS_LIT expression
                        | expression TIMES_LIT expression
                        | expression DIVIDE_LIT expression
                        | expression EXP_LIT expression
    """
    if p[2] == '+' or p[2] == 'plus':
        p[0] = p[1] + p[3]
    elif p[2] == '-' or p[2] == 'minus':
        p[0] = p[1] - p[3]
    elif p[2] == '*' or p[2] == 'times':
        p[0] = p[1] * p[3]
    elif p[2] == '/' or p[2] == 'divide':
        p[0] = p[1] / p[3]
    elif p[2] == '**' or p[2] == 'power':
        p[0] = p[1] ** p[3]


def p_expression_uminus(p):
    """expression : MINUS expression %prec UMINUS
                                | MINUS_LIT expression %prec UMINUS"""
    p[0] = -p[2]


def p_expression_group(p):
    """expression : LPAREN expression RPAREN"""
    p[0] = p[2]


def p_expression_number(p):
    """expression : NUMBER"""
    p[0] = p[1]


def p_expression_name(p):
    """expression : NAME"""
    try:
        p[0] = p[1]
    except LookupError:
        print("Undefined name '%s'" % p[1])
        p[0] = 0


def p_error(p):
    if p:
        print("syntax error at {0}".format(p.value))
    else:
        print("syntax error at EOF")


def process(data):
    lex.lex()
    yacc.yacc()
    yacc.parse(data)


if __name__ == "__main__":
    print("Enter the Equation")
    data = sys.stdin.readline()
    process(data)
