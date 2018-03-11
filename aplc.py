#!/usr/bin/python3

import sys
import ply.lex as lex
import ply.yacc as yacc

########################################################################################

input_file_name = ''
pointer_id_list = []
static_id_list = []
no_assignments = 0
temp_pk = 0


def get_next_temp_pk():
    global temp_pk
    prev_tpk = temp_pk
    temp_pk += 1
    return 't%d' % prev_tpk


def generate_CFG_for_expression(expression_node):
    """
    Note:
        1. Expression node has exactly two children
        2. A term is also an expression
        3. If the node is not a term then it is a subtree ending in term leaves
    """
    if len(expression_node.children) == 2:
        lhs = expression_node.children[0]
        rhs = expression_node.children[1]
        if lhs.is_term() and rhs.is_term():
            ret_temp_id = get_next_temp_pk()
            this_cfg = '%s = %s %s %s\n' % (ret_temp_id, lhs.value, expression_node.value, rhs.value)
            return ret_temp_id, this_cfg
        elif not lhs.is_term() and rhs.is_term():
            temp_id, lhs_cfg = generate_CFG_for_expression(lhs)
            ret_temp_id = get_next_temp_pk()
            this_cfg = '%s = %s %s %s\n' % (ret_temp_id, temp_id, expression_node.value, rhs.value)
            return ret_temp_id, lhs_cfg + this_cfg
        elif lhs.is_term() and not rhs.is_term():
            temp_id, rhs_cfg = generate_CFG_for_expression(rhs)
            ret_temp_id = get_next_temp_pk()
            this_cfg = '%s = %s %s %s\n' % (ret_temp_id, lhs.value, expression_node.value, temp_id)
            return ret_temp_id, rhs_cfg + this_cfg
        else:
            temp_id_lhs, lhs_cfg = generate_CFG_for_expression(lhs)
            temp_id_rhs, rhs_cfg = generate_CFG_for_expression(rhs)
            ret_temp_id = get_next_temp_pk()
            this_cfg = '%s = %s %s %s\n' % (ret_temp_id, temp_id_lhs, expression_node.value, temp_id_rhs)
            return ret_temp_id, lhs_cfg + rhs_cfg + this_cfg
    elif len(expression_node.children) == 1:
        child_node = expression_node.children[0]
        if child_node.is_term():
            ret_temp_id = get_next_temp_pk()
            this_cfg = '%s = %s%s\n' % (ret_temp_id, expression_node.value, child_node.value)
            return ret_temp_id, this_cfg
        else:
            temp_id, child_cfg = generate_CFG_for_expression(child_node)
            ret_temp_id = get_next_temp_pk()
            this_cfg = '%s = %s%s\n' % (ret_temp_id, expression_node.value, temp_id)
            return ret_temp_id, child_cfg + this_cfg


def generate_CFG(node):
    cfg = ''
    if node.type == 'BODY':
        cfg += '<bb %d>\n' % -1
        for child in node.children:
            # Assignment
            if child.type == 'ASGN':
                asgn = child
                lhs = asgn.children[0]
                rhs = asgn.children[1]
                if rhs.is_term():
                    cfg += '%s = %s\n' % (lhs.value, rhs.value)
                else:
                    temp_id, rhs_cfg = generate_CFG_for_expression(rhs)
                    this_cfg = '%s = %s\n' % (lhs.value, temp_id)
                    cfg += rhs_cfg + this_cfg

    cfg += '<bb %d>\n' % -1
    cfg += 'End\n'
    return cfg


class ASTNode:
    def __init__(self, _type, value, is_constant=False):
        self.type = _type
        self.value = value
        self.children = []
        self.is_constant = is_constant


    def add_child(self, child):
        self.children.append(child)


    def is_term(self):
        """
        Returns whether the token stream comming from this node is a term or not.
        """
        if self.type == 'VAR' \
            or self.type == 'CONST' \
            or self.type == 'DEREF' \
            or self.type == 'ADDR':
            return True
        else:
            return False


    def text_repr(self, tabs):
        ans = ''
        if self.type == 'VAR' or self.type == 'CONST':
            ans += '\t' * tabs + str(self.type) + '(' + str(self.value) + ')' + '\n'
        elif self.type == 'BODY':
            for i in range(len(self.children)):
                ans += self.children[i].text_repr(tabs)
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
    'if': 'IF',
    'else': 'ELSE',
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
    'PLUS', 'MINUS',
    'DIVIDE',
    'GT', 'LT', 'GE', 'LE', 'EE', 'NE',
    'LOGICAL_AND', 'LOGICAL_OR',

]

tokens = tokens + list(reserved_keywords.values())

t_ignore = ' \t'
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_PLUS = r'\+'
t_MINUS = r'-'
t_DIVIDE = r'/'
t_ASTERISK = r'\*'
t_AMPERSAND = r'&'
t_SEMICOLON = r';'
t_COMMA = r','
t_NE = r'!='
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

t_LOGICAL_AND = r'&&'
t_LOGICAL_OR = r'\|\|'


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
    ('left', 'LOGICAL_OR'),
    ('left', 'LOGICAL_AND'),
    ('left', 'EE', 'NE',),
    ('left', 'LT', 'GT', 'LE', 'GE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'ASTERISK', 'DIVIDE'),
    ('right', 'U_MINUS'),
    ('right', 'ADDR_OF', 'DE_REF'),
)


def p_code(p):
    """code : VOID MAIN L_PAREN R_PAREN L_CURLY body R_CURLY"""
    body = p[6]
    with open(input_file_name + '.ast1', 'w') as the_file:
        the_file.write(body.text_repr(0))
    cfg = generate_CFG(body)
    with open(input_file_name + '.cfg1', 'w') as the_file:
        the_file.write(cfg)


def p_body(p):
    """
    body : statement SEMICOLON body
            | while_block body
            | if_block body
            |
    """
    if len(p) == 1:
        body = ASTNode('BODY', 'body')
    elif len(p) == 3:
        body = p[2]
        body.children = [p[1]] + body.children
    elif len(p) == 4:
        body = p[3]
        if p[1] is not None:
            body.children = [p[1]] + body.children

    p[0] = body

# -------------------------------- CONDITION --------------------------------
def p_compound_condition(p):
    """
    compound_condition : compound_condition LOGICAL_AND compound_condition
                       | compound_condition LOGICAL_OR compound_condition
                       | L_PAREN compound_condition R_PAREN
                       | condition
    """
    if len(p) == 4:
        if p[2] == '&&':
            node = ASTNode('AND', '&&', p[1].is_constant and p[3].is_constant)
            node.add_child(p[1])
            node.add_child(p[3])
            p[0] = node
        elif p[2] == '||':
            node = ASTNode('OR', '||', p[1].is_constant and p[3].is_constant)
            node.add_child(p[1])
            node.add_child(p[3])
            p[0] = node
        elif p[1] == '(' and p[3] == ')':
            p[0] = p[2]
    elif len(p) == 2:
        p[0] = p[1]


def p_condition(p):
    """
    condition : expression EE expression
                | expression NE expression
                | expression GE expression
                | expression GT expression
                | expression LE expression
                | expression LT expression
    """
    if p[2] == '==':
        node = ASTNode('EQ', '==', p[1].is_constant and p[3].is_constant)
        node.add_child(p[1])
        node.add_child(p[3])
        p[0] = node
    elif p[2] == '!=':
        node = ASTNode('NE', '!=', p[1].is_constant and p[3].is_constant)
        node.add_child(p[1])
        node.add_child(p[3])
        p[0] = node
    elif p[2] == '>=':
        node = ASTNode('GE', '>=', p[1].is_constant and p[3].is_constant)
        node.add_child(p[1])
        node.add_child(p[3])
        p[0] = node
    elif p[2] == '>':
        node = ASTNode('GT', '>', p[1].is_constant and p[3].is_constant)
        node.add_child(p[1])
        node.add_child(p[3])
        p[0] = node
    elif p[2] == '<=':
        node = ASTNode('LE', '<=', p[1].is_constant and p[3].is_constant)
        node.add_child(p[1])
        node.add_child(p[3])
        p[0] = node
    elif p[2] == '<':
        node = ASTNode('LT', '<', p[1].is_constant and p[3].is_constant)
        node.add_child(p[1])
        node.add_child(p[3])
        p[0] = node


# -------------------------------- WHILE BLOCK --------------------------------
def p_while_block(p):
    """
    while_block : WHILE L_PAREN compound_condition R_PAREN if_else_while_body
    """
    while_block = ASTNode('WHILE', 'while')
    while_block.add_child(p[3])
    while_block.add_child(p[5])
    p[0] = while_block


# -------------------------------- IF BLOCK --------------------------------
def p_if_block(p):
    """
    if_block : IF L_PAREN compound_condition R_PAREN if_else_while_body
                | IF L_PAREN compound_condition R_PAREN if_else_while_body ELSE if_else_while_body
                | IF L_PAREN compound_condition R_PAREN if_else_while_body ELSE if_block
    """
    if_block = ASTNode('IF', 'if')
    if_block.add_child(p[3])
    if_block.add_child(p[5])
    if len(p) == 8:
        if_block.add_child(p[7])
    p[0] = if_block


# -------------------------------- IF ELSE WHILE COMMON BODY --------------------------------
def p_if_else_while_body(p):
    """
    if_else_while_body : SEMICOLON
                | assignment SEMICOLON
                | L_CURLY body R_CURLY
    """
    if len(p) == 2:
        p[0] = ASTNode('BODY', 'body')
    elif len(p) == 3:
        body = ASTNode('BODY', 'body')
        body.add_child(p[1])
        p[0] = body
    elif len(p) == 4:
        p[0] = p[2]


# -------------------------------- STATEMENT --------------------------------
def p_statement(p):
    """
    statement : INT dlist
                | assignment
    """
    if len(p) == 2:
        p[0] = p[1]


# -------------------------------- DECLARATION --------------------------------
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


# -------------------------------- ASSIGNMENT --------------------------------
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
        asterisk_node = ASTNode('DEREF', '*%s' % p[2].value)
        asterisk_node.add_child(p[2])
        node = ASTNode('ASGN', '=')
        node.add_child(asterisk_node)
        node.add_child(p[4])
        p[0] = node


# -------------------------------- EXPRESSION --------------------------------
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


# -------------------------------- TERM --------------------------------
def p_term(p):
    """
    term : ASTERISK term %prec DE_REF
        | AMPERSAND term %prec ADDR_OF
        | ID

    """
    if len(p) == 2:
        p[0] = ASTNode('VAR', p[1])
    elif len(p) == 3:
        if p[1] == '*':
            node = ASTNode('DEREF', '*%s' % p[2].value)
            node.add_child(p[2])
            p[0] = node
        elif p[1] == '&':
            node = ASTNode('ADDR', '&%s' % p[2].value)
            node.add_child(p[2])
            p[0] = node

# -------------------------------- ERROR --------------------------------
def p_error(p):
    if p:
        print("syntax error at {0} in line {1}".format(p.value, p.lineno))
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
