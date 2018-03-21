import sys
import ply.lex as lex
import ply.yacc as yacc
from util import ASTNode, generate_CFG

########################################################################################

input_file_name = ''
no_assignments = 0

########################################################################################

reserved_keywords = {
    'void': 'VOID',
    'main': 'MAIN',
    'int': 'INT',
    'while': 'WHILE',
    'if': 'IF',
    'float': 'FLOAT',
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
    'INT_LIT',
    'FLOAT_LIT',
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


def t_FLOAT_LIT(t):
    r'\d+\.\d*'
    try:
        t.value = float(t.value)
    except ValueError:
        print("Float value too large %f", t.value)
        t.value = 0
    return t


def t_INT_LIT(t):
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


# def p_code(p):
#     """code : global_dlist func_list VOID MAIN L_PAREN R_PAREN L_CURLY body R_CURLY"""
#     body = p[8]
#     with open(input_file_name + '.ast', 'w') as the_file:
#         the_file.write('\n' * no_assignments + body.tree_text_repr(0))

#     cfg = generate_CFG(body)
#     with open(input_file_name + '.cfg', 'w') as the_file:
#         the_file.write('\n' + cfg.tree_text_repr())

# -------------------------------- CODE --------------------------------
def p_code(p):
    """
    code : global_dlist code
        | function code
        |
    """
    pass


# -------------------------------- GLOBALS --------------------------------
def p_global_dlist(p):
    """
    global_dlist : type dlist SEMICOLON
    """
    pass


# -------------------------------- FUNCTION --------------------------------
def p_function(p):
    """
    function : type return_term L_PAREN param_list R_PAREN L_CURLY body R_CURLY
            | type return_term L_PAREN param_list R_PAREN SEMICOLON
            | VOID void_id L_PAREN param_list R_PAREN L_CURLY body R_CURLY
            | VOID void_id L_PAREN param_list R_PAREN SEMICOLON
    """
    pass


def p_void_id(p):
    """
    void_id : ID
            | MAIN
    """
    pass


def p_return_term(p):
    """
    return_term : function_term
    """
    pass


def p_param_list(p):
    """
    param_list : param_list_non_empty
                |
    """
    pass


def p_param_list_non_empty(p):
    """
    param_list_non_empty : type function_term COMMA param_list_non_empty
            | type function_term
    """
    pass


def p_function_term(p):
    """
    function_term : ASTERISK function_term_r
    """
    pass


def p_function_term_r(p):
    """
    function_term_r : ASTERISK function_term_r
                        | ID
    """
    pass


# -------------------------------- BODY --------------------------------
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
        body.prepend_child(p[1])
    elif len(p) == 4:
        body = p[3]
        if p[1] is not None:
            p[1].parent = body
            body.prepend_child(p[1])

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
    while_block : WHILE L_PAREN compound_condition R_PAREN if_else_while_common_body
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
    if_block : IF L_PAREN compound_condition R_PAREN if_else_while_common_body
                | IF L_PAREN compound_condition R_PAREN if_else_while_common_body ELSE if_block
                | IF L_PAREN compound_condition R_PAREN if_else_while_common_body ELSE if_else_while_common_body
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
def p_if_else_while_common_body(p):
    """
    if_else_while_common_body : SEMICOLON
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
    statement : type dlist
                | assignment
    """
    if len(p) == 2:
        p[0] = p[1]


# -------------------------------- DECLARATION --------------------------------
def p_type(p):
    """
    type : INT
        | FLOAT
    """
    pass


def p_dlist(p):
    """
    dlist : declaration COMMA dlist
            | declaration
    """
    pass


def p_declaration(p):
    """
    declaration : ID
                | ASTERISK declaration %prec DE_REF
    """
    pass


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
def p_expression_function_call(p):
    """
    expression : ID L_PAREN arg_list R_PAREN
    """
    function_call = ASTNode('FUNCTION', 'function')
    id_node = ASTNode('VAR', p[1])
    id_node.parent = function_call
    function_call.add_child(id_node)
    arg_list = p[3]
    arg_list.parent = function_call
    function_call.add_child(arg_list)
    p[0] = function_call


def p_arg_list(p):
    """
    arg_list : arg_list_non_empty
            |
    """
    if len(p) == 1:
        p[0] = ASTNode('PARAM_LIST', 'param_list')
    elif len(p) == 2:
        p[0] = p[1]


def p_arg_list_non_empty(p):
    """
    arg_list_non_empty : term COMMA arg_list_non_empty
                    | term
    """
    if len(p) == 2:
        param_list = ASTNode('PARAM_LIST', 'param_list')
        p[1].parent = param_list
        param_list.add_child(p[1])
    elif len(p) == 4:
        param_list = p[3]
        p[1].parent = param_list
        param_list.prepend_child(p[1])

    p[0] = param_list


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


def p_expression_int_lit(p):
    """expression : INT_LIT"""
    p[0] = ASTNode('CONST', p[1], True)


def p_expression_float_lit(p):
    """expression : FLOAT_LIT"""
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
