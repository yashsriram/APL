#!/usr/bin/python3

import sys
import ply.lex as lex
import ply.yacc as yacc

########################################################################################

input_file_name = ''
pointer_id_list = []
static_id_list = []
no_assignments = 0
assignment_list = []


class ASTNode:
    def __init__(self, _type, value, is_constant=False):
        self.type = _type
        self.value = value
        self.children = []
        self.is_constant = is_constant

    def add_child(self, child):
        self.children.append(child)

    def text_repr(self, tabs):
        ans = ''
        if self.type == 'VAR' or self.type == 'CONST':
            ans += '\t' * tabs + str(self.type) + '(' + str(self.value) + ')' + '\n'
        else:
            ans += '\t' * tabs + str(self.type) + '\n'
            ans += '\t' * tabs + '(' + '\n'
            for i in range(len(self.children)):
                ans += self.children[i].text_repr(tabs + 1)
                # Don't print last ,
                if i != len(self.children) - 1:
                    ans += '\t' * (tabs + 1) + ',' + '\n'
            ans += '\t' * tabs + ')' + '\n'
        return ans


########################################################################################

reserved_keywords = {
    'void': 'VOID',
    'main': 'MAIN',
    'int': 'INT',
    'while': 'WHILE',
}

tokens = [
    'ID',
    'L_PAREN', 'R_PAREN',
    'L_CURLY', 'R_CURLY',
    'SEMICOLON',
    'COMMA',
    'EQUALS',
    'AMPERSAND', 'ASTERISK',
    'NUMBER',
    'PLUS', 'MINUS',
    'DIVIDE',
    'GT', 'LT', 'GE', 'LE', 'EE'
]

tokens = tokens + list(reserved_keywords.values())

t_ignore = ' \t\n'

t_PLUS = r'\+'
t_MINUS = r'-'
t_DIVIDE = r'/'
t_ASTERISK = r'\*'
t_AMPERSAND = r'&'
t_SEMICOLON = r';'
t_COMMA = r','
t_EE = r'=='
t_EQUALS = r'='
t_L_CURLY = r'{'
t_R_CURLY = r'}'
t_L_PAREN = r'\('
t_R_PAREN = r'\)'

t_GE = r'>='
t_GT = r'>'
t_LE = r'<='
t_LT = r'<'



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
    ('left', 'PLUS', 'MINUS'),
    ('left', 'ASTERISK', 'DIVIDE'),
    ('right', 'U_MINUS'),
    ('right', 'AMPERSAND', 'DE_REF'),
)


def p_code(p):
    """code : VOID MAIN L_PAREN R_PAREN L_CURLY body R_CURLY"""
    # print(len(static_id_list))
    # print(len(pointer_id_list))
    # print(no_assignments)
    with open('Parser_ast_' + input_file_name + '.txt', 'w') as the_file:
        for assignment in assignment_list:
            the_file.write(assignment.text_repr(0) + '\n')


def p_body(p):
    """
    body : statement SEMICOLON body
            | WHILE L_PAREN condition R_PAREN while_body body
            |
    """
    pass


def p_statement(p):
    """
    statement : INT dlist
                | assignment
    """
    if len(p) == 2:
        global assignment_list
        assignment_list.append(p[1])


def p_dlist(p):
    """
    dlist : declaration COMMA dlist
            | declaration
    """
    pass


def p_static_declaration(p):
    """
    declaration : ID
    """
    static_id_list.append(p[1])


def p_pointer_declaration(p):
    """
    declaration : ASTERISK pointer_declaration %prec DE_REF
    """
    pass


def p_r_pointer_declaration(p):
    """
    pointer_declaration : ASTERISK pointer_declaration %prec DE_REF
                        | ID
    """
    if len(p) == 2:
        pointer_id_list.append(p[1])


def p_assignment(p):
    """
    assignment :  ID EQUALS expression
                | ASTERISK term EQUALS expression %prec DE_REF
    """
    global no_assignments
    no_assignments += 1
    if len(p) == 4:
        if p[3].is_constant:
            print("Error id = constant")
            raise SyntaxError
        id_node = ASTNode('VAR', p[1])
        node = ASTNode('ASGN', '=')
        node.add_child(id_node)
        node.add_child(p[3])
        p[0] = node
    elif len(p) == 5:
        asterisk_node = ASTNode('DEREF', '*')
        asterisk_node.add_child(p[2])
        node = ASTNode('ASGN', '=')
        node.add_child(asterisk_node)
        node.add_child(p[4])
        p[0] = node


def p_condition(p):
    """
    condition : expression EE expression
                | expression GE expression
                | expression GT expression
                | expression LE expression
                | expression LT expression
    """
    pass


def p_while_body(p):
    """
    while_body : assignment SEMICOLON
                | L_CURLY body R_CURLY
    """
    pass


def p_expression_binary_op(p):
    """
    expression : expression PLUS expression
              | expression MINUS expression
              | expression ASTERISK expression
              | expression DIVIDE expression
    """
    if p[2] == '+':
        node = ASTNode('PLUS', '+', p[1].is_constant and p[3].is_constant)
        node.add_child(p[1])
        node.add_child(p[3])
        p[0] = node
    elif p[2] == '-':
        node = ASTNode('MINUS', '-', p[1].is_constant and p[3].is_constant)
        node.add_child(p[1])
        node.add_child(p[3])
        p[0] = node
    elif p[2] == '*':
        node = ASTNode('MUL', '*', p[1].is_constant and p[3].is_constant)
        node.add_child(p[1])
        node.add_child(p[3])
        p[0] = node
    elif p[2] == '/':
        node = ASTNode('DIV', '/', p[1].is_constant and p[3].is_constant)
        node.add_child(p[1])
        node.add_child(p[3])
        p[0] = node


def p_expression_uminus(p):
    """expression : MINUS expression %prec U_MINUS"""
    node = ASTNode('UMINUS', '-', p[2].is_constant)
    node.add_child(p[2])
    p[0] = node


def p_expression_group(p):
    """expression : L_PAREN expression R_PAREN"""
    p[0] = p[2]


def p_expression_number(p):
    """expression : NUMBER"""
    p[0] = ASTNode('CONST', p[1], True)


def p_expression_term(p):
    """expression : term"""
    p[0] = p[1]


def p_term(p):
    """
    term : ASTERISK term %prec DE_REF
        | AMPERSAND term
        | ID

    """
    if len(p) == 2:
        p[0] = ASTNode('VAR', p[1])
    elif len(p) == 3:
        if p[1] == '*':
            node = ASTNode('DEREF', '*')
            node.add_child(p[2])
            p[0] = node
        elif p[1] == '&':
            node = ASTNode('ADDR', '&')
            node.add_child(p[2])
            p[0] = node


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
    if len(sys.argv) != 2:
        print('Usage :', sys.argv[0], 'source_file_path')
        exit(-1)
    input_file_name = sys.argv[1]
    source_code_file = open(input_file_name, 'r')
    source_code = ''
    for line in source_code_file:
        source_code += line
    # print(source_code)
    process(source_code)
    source_code_file.close()
