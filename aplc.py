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
block_pk = 1


def get_next_block_pk():
    global block_pk
    prev_bpk = block_pk
    block_pk += 1
    return prev_bpk


def get_next_temp_pk():
    global temp_pk
    prev_tpk = temp_pk
    temp_pk += 1
    return 't%d' % prev_tpk


def generate_block_text_recr(expression_node):
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
            temp_id, lhs_cfg = generate_block_text_recr(lhs)
            ret_temp_id = get_next_temp_pk()
            this_cfg = '%s = %s %s %s\n' % (ret_temp_id, temp_id, expression_node.value, rhs.value)
            return ret_temp_id, lhs_cfg + this_cfg
        elif lhs.is_term() and not rhs.is_term():
            temp_id, rhs_cfg = generate_block_text_recr(rhs)
            ret_temp_id = get_next_temp_pk()
            this_cfg = '%s = %s %s %s\n' % (ret_temp_id, lhs.value, expression_node.value, temp_id)
            return ret_temp_id, rhs_cfg + this_cfg
        else:
            temp_id_lhs, lhs_cfg = generate_block_text_recr(lhs)
            temp_id_rhs, rhs_cfg = generate_block_text_recr(rhs)
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
            temp_id, child_cfg = generate_block_text_recr(child_node)
            ret_temp_id = get_next_temp_pk()
            this_cfg = '%s = %s%s\n' % (ret_temp_id, expression_node.value, temp_id)
            return ret_temp_id, child_cfg + this_cfg


def generate_block_text(cfg_node):
    cfg = ''
    if cfg_node.type == 'ASGN_BLOCK':
        cfg += '<bb %d>\n' % cfg_node.block_number
        for child in cfg_node.value:
            # Assignment
            asgn = child
            lhs = asgn.children[0]
            rhs = asgn.children[1]
            if rhs.is_term():
                cfg += '%s = %s\n' % (lhs.value, rhs.value)
            else:
                temp_id, rhs_cfg = generate_block_text_recr(rhs)
                this_cfg = '%s = %s\n' % (lhs.value, temp_id)
                cfg += rhs_cfg + this_cfg
    elif cfg_node.type == 'CONDITION_BLOCK':
        cfg += '<bb %d>\n' % cfg_node.block_number
        temp_id, child_cfg = generate_block_text_recr(cfg_node.value)
        cfg += child_cfg

    cfg += '\n'
    return cfg


def generate_CFG(ast_node):
    if ast_node.type == 'BODY':
        cfg_node = CFGNode(ast_node.type, ast_node.value, ast_node.is_constant, ast_node.parent)
        block_siblings = []
        for child in ast_node.children:
            if child.type == 'ASGN':
                block_siblings.append(child)
            else:
                # Merge all contiguous assignment statements into one MASTNode
                if len(block_siblings) != 0:
                    assign_block = CFGNode('ASGN_BLOCK', block_siblings, parent=cfg_node, block_number=get_next_block_pk())
                    cfg_node.add_child(assign_block)
                    print(generate_block_text(assign_block))
                    block_siblings = []
                # Handle the odd child
                if child.type == 'IF':
                    # If node
                    if_cfg_node = generate_CFG(child)
                    if_cfg_node.parent = cfg_node
                    cfg_node.add_child(if_cfg_node)
                elif child.type == 'WHILE':
                    # While node
                    while_cfg_node = generate_CFG(child)
                    # Attach While node to cfg_node
                    while_cfg_node.parent = cfg_node
                    cfg_node.add_child(while_cfg_node)

        # Merge all contiguous assignment statements into one MASTNode
        if len(block_siblings) != 0:
            assign_block = CFGNode('ASGN_BLOCK', block_siblings, parent=cfg_node, block_number=get_next_block_pk())
            cfg_node.add_child(assign_block)
            print(generate_block_text(assign_block))

        return cfg_node
    elif ast_node.type == 'IF':
        if_statement = ast_node
        if_cfg_node = CFGNode('IF_BLOCK', if_statement.value, if_statement.is_constant)
        # Compound condition node
        cc_cfg_node = CFGNode('CONDITION_BLOCK',if_statement.children[0], block_number=get_next_block_pk())
        cc_cfg_node.parent = if_cfg_node
        if_cfg_node.add_child(cc_cfg_node)
        print(generate_block_text(cc_cfg_node))
        # If body node
        if_body = if_statement.children[1]
        if_body_cfg_node = generate_CFG(if_body)
        if_body_cfg_node.parent = if_cfg_node
        if_cfg_node.add_child(if_body_cfg_node)
        # Else body node
        if len(if_statement.children) == 3:
            else_body = if_statement.children[2]
            else_body_cfg_node = generate_CFG(else_body)
            else_body_cfg_node.parent = if_cfg_node
            if_cfg_node.add_child(else_body_cfg_node)
        return if_cfg_node
    elif ast_node.type == 'WHILE':
        while_statement = ast_node
        while_cfg_node = CFGNode('WHILE_BLOCK', while_statement.value, while_statement.is_constant)
        # Compound condition node
        cc_cfg_node = CFGNode('CONDITION_BLOCK',while_statement.children[0], block_number=get_next_block_pk())
        cc_cfg_node.parent = while_cfg_node
        while_cfg_node.add_child(cc_cfg_node)
        print(generate_block_text(cc_cfg_node))
        # While body node
        while_body = while_statement.children[1]
        while_body_cfg_node = generate_CFG(while_body)
        while_body_cfg_node.parent = while_cfg_node
        while_cfg_node.add_child(while_body_cfg_node)
        return while_cfg_node        



class CFGNode:
    """
    Nodes are list of assignments or a compound_condition
    """
    def __init__(self, _type, value, is_constant=False, parent=None, block_number=None):
        self.type = _type
        self.value = value
        self.parent = parent
        self.is_constant = is_constant
        self.children = []
        self.block_number = block_number

    def add_child(self, child):
        self.children.append(child)


class ASTNode:
    def __init__(self, _type, value, is_constant=False, parent=None):
        self.type = _type
        self.value = value
        self.parent = parent
        self.is_constant = is_constant
        self.children = []


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
    'LOGICAL_AND', 'LOGICAL_OR', 'EXCLAMATION'

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
t_EXCLAMATION = r'!'


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

    # cfg = generate_block_text(body)
    # with open(input_file_name + '.cfg1', 'w') as the_file:
    #     the_file.write(cfg)


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
        p[1].parent = body    
        body.children = [p[1]] + body.children
    elif len(p) == 4:
        body = p[3]
        if p[1] is not None:
            p[1].parent = body
            body.children = [p[1]] + body.children

    p[0] = body

# -------------------------------- CONDITION --------------------------------
def p_compound_condition(p):
    """
    compound_condition : compound_condition LOGICAL_AND compound_condition
                       | compound_condition LOGICAL_OR compound_condition
                       | L_PAREN compound_condition R_PAREN
                       | EXCLAMATION condition
                       | condition
    """
    if len(p) == 4:
        if p[2] == '&&':
            node = ASTNode('AND', '&&', p[1].is_constant and p[3].is_constant)
            p[1].parent = node
            node.add_child(p[1])
            p[3].parent = node
            node.add_child(p[3])
            p[0] = node
        elif p[2] == '||':
            node = ASTNode('OR', '||', p[1].is_constant and p[3].is_constant)
            p[1].parent = node
            node.add_child(p[1])
            p[3].parent = node
            node.add_child(p[3])
            p[0] = node
        elif p[1] == '(' and p[3] == ')':
            p[0] = p[2]
    elif len(p) == 3:
        node = ASTNode('NOT', '!', p[2].is_constant)
        p[2].parent = node
        node.add_child(p[2])
        p[0] = node
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
        p[1].parent = node
        node.add_child(p[1])
        p[3].parent = node
        node.add_child(p[3])
        p[0] = node
    elif p[2] == '!=':
        node = ASTNode('NE', '!=', p[1].is_constant and p[3].is_constant)
        p[1].parent = node
        node.add_child(p[1])
        p[3].parent = node
        node.add_child(p[3])
        p[0] = node
    elif p[2] == '>=':
        node = ASTNode('GE', '>=', p[1].is_constant and p[3].is_constant)
        p[1].parent = node
        node.add_child(p[1])
        p[3].parent = node
        node.add_child(p[3])
        p[0] = node
    elif p[2] == '>':
        node = ASTNode('GT', '>', p[1].is_constant and p[3].is_constant)
        p[1].parent = node
        node.add_child(p[1])
        p[3].parent = node
        node.add_child(p[3])
        p[0] = node
    elif p[2] == '<=':
        node = ASTNode('LE', '<=', p[1].is_constant and p[3].is_constant)
        p[1].parent = node
        node.add_child(p[1])
        p[3].parent = node
        node.add_child(p[3])
        p[0] = node
    elif p[2] == '<':
        node = ASTNode('LT', '<', p[1].is_constant and p[3].is_constant)
        p[1].parent = node
        node.add_child(p[1])
        p[3].parent = node
        node.add_child(p[3])
        p[0] = node


# -------------------------------- WHILE BLOCK --------------------------------
def p_while_block(p):
    """
    while_block : WHILE L_PAREN compound_condition R_PAREN if_else_while_body
    """
    while_block = ASTNode('WHILE', 'while')
    p[3].parent = while_block
    while_block.add_child(p[3])
    p[5].parent = while_block
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
    p[3].parent = if_block
    if_block.add_child(p[3])
    p[5].parent = if_block
    if_block.add_child(p[5])
    if len(p) == 8:
        p[7].parent = if_block
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
        p[1].parent = body
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
        id_node.parent = node
        node.add_child(id_node)
        p[3].parent = node
        node.add_child(p[3])
        p[0] = node
    elif len(p) == 5:
        asterisk_node = ASTNode('DEREF', '*%s' % p[2].value)
        p[2].parent = asterisk_node
        asterisk_node.add_child(p[2])
        node = ASTNode('ASGN', '=')
        asterisk_node.parent = node
        node.add_child(asterisk_node)
        p[4].parent = node
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
        p[1].parent = node
        node.add_child(p[1])
        p[3].parent = node
        node.add_child(p[3])
        p[0] = node
    elif p[2] == '-':
        node = ASTNode('MINUS', '-', p[1].is_constant and p[3].is_constant)
        p[1].parent = node
        node.add_child(p[1])
        p[3].parent = node
        node.add_child(p[3])
        p[0] = node
    elif p[2] == '*':
        node = ASTNode('MUL', '*', p[1].is_constant and p[3].is_constant)
        p[1].parent = node
        node.add_child(p[1])
        p[3].parent = node
        node.add_child(p[3])
        p[0] = node
    elif p[2] == '/':
        node = ASTNode('DIV', '/', p[1].is_constant and p[3].is_constant)
        p[1].parent = node
        node.add_child(p[1])
        p[3].parent = node
        node.add_child(p[3])
        p[0] = node


def p_expression_uminus(p):
    """expression : MINUS expression %prec U_MINUS"""
    node = ASTNode('UMINUS', '-', p[2].is_constant)
    p[2].parent = node
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
            p[2].parent = node
            node.add_child(p[2])
            p[0] = node
        elif p[1] == '&':
            node = ASTNode('ADDR', '&%s' % p[2].value)
            p[2].parent = node
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
