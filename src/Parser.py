import sys
import ply.lex as lex
import ply.yacc as yacc
from utils.astutils import ASTNode
from utils.cfgutils import generate_cfg
from utils.symbolutils import get_non_func_symbol_from_stack, SymbolTable, Symbol, procedure_table_text_repr, variable_table_text_repr

########################################################################################

input_file_name = ''
no_assignments = 0
symbol_table_stack = []
global_symbol_table = SymbolTable()

########################################################################################

reserved_keywords = {
    'void': 'VOID',
    'main': 'MAIN',
    'int': 'INT',
    'while': 'WHILE',
    'if': 'IF',
    'float': 'FLOAT',
    'else': 'ELSE',
    'return': 'RETURN',
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


# -------------------------------- INITIAL PRODUCTION --------------------------------
def p_initial_production(p):
    """initial_production : code"""
    code_node = p[1]
    with open(input_file_name + '.ast', 'w') as output_file:
        for child in code_node.children:
            output_file.write(child.tree_text_repr())

    with open(input_file_name + '.cfg', 'w') as output_file:
        for child in code_node.children:
            cfg = generate_cfg(child)
            output_file.write(cfg.tree_text_repr())

    # print(procedure_table_text_repr(global_symbol_table))
    with open(input_file_name + '.sym', 'w') as output_file:
        output_file.write(procedure_table_text_repr(global_symbol_table))
        output_file.write(variable_table_text_repr(global_symbol_table,'global'))


# -------------------------------- CODE --------------------------------
def p_code(p):
    """
    code : global_dlist code
        | function code
        |
    """
    if len(p) == 1:
        p[0] = ASTNode('CODE', 'code')
    elif len(p) == 3 and p[1] is not None:
        code_node = p[2]
        ast_node = p[1]
        code_node.prepend_child(ast_node)
        p[0] = code_node
    else:
        p[0] = p[2]


# -------------------------------- GLOBALS --------------------------------
def p_global_dlist(p):
    """
    global_dlist : type dlist SEMICOLON
    """
    global global_symbol_table
    _type = p[1]
    dlist = p[2]
    for declaration in dlist:
        _id, deref_depth = declaration
        if not global_symbol_table.symbol_exists(_id):
            symbol = Symbol(_id, _type, Symbol.GLOBAL_SCOPE, deref_depth, 4)
            global_symbol_table.add_symbol(symbol)
        else:
            panic('Symbol already exists')
    p[0] = None


# -------------------------------- FUNCTION --------------------------------
def p_function_prototype(p):
    """
    function : function_head L_PAREN param_list R_PAREN SEMICOLON
    """
    global symbol_table_stack
    global global_symbol_table
    current_symbol_table = symbol_table_stack[-1]
    type_node, id_node, _id, _type, deref_depth = p[1]
    if not global_symbol_table.symbol_exists(_id):
        symbol = Symbol(_id, _type, Symbol.GLOBAL_SCOPE, deref_depth, 0, its_table=current_symbol_table,
                        is_prototype=True)
        global_symbol_table.add_symbol(symbol)
        symbol_table_stack.pop()
    else:
        panic('Function prototype : Symbol already exists')
    p[0] = None


def p_function_implementation(p):
    """
    function : function_head L_PAREN param_list R_PAREN L_CURLY body return_statement R_CURLY
    """
    global symbol_table_stack
    global global_symbol_table
    current_symbol_table = symbol_table_stack[-1]
    type_node, id_node, _id, _type, deref_depth = p[1]
    param_list_node = p[3]
    body_node = p[6]
    return_node, return_existence = p[7]
    if _id == 'main':
        if len(param_list_node.children) != 0:
            panic('main function cannot have parameters')
        if return_existence:
            panic('main function cannot have return statement')
    if not global_symbol_table.symbol_exists(_id):
        # New function implementation
        symbol = Symbol(_id, _type, Symbol.GLOBAL_SCOPE, deref_depth, 0, its_table=current_symbol_table,
                        is_prototype=False)
        global_symbol_table.add_symbol(symbol)
        symbol_table_stack.pop()
    else:
        existing_symbol = global_symbol_table.get_symbol(_id)
        if not existing_symbol.is_function():
            # Existing symbol is not a function
            panic('Function implementation : Symbol already exists')
        else:
            if existing_symbol.is_prototype:
                if existing_symbol.type == _type and existing_symbol.deref_depth == deref_depth:
                    param_symbols1 = current_symbol_table.get_param_signature()
                    param_symbols2 = existing_symbol.its_table.get_param_signature()
                    if param_symbols1 == param_symbols2:
                        symbol = Symbol(_id, _type, Symbol.GLOBAL_SCOPE, deref_depth, 0,
                                        its_table=current_symbol_table,
                                        is_prototype=False)
                        global_symbol_table.add_symbol(symbol)
                        symbol_table_stack.pop()
                    else:
                        # Params mismatch
                        panic('Params mismatch in function implementation')
                else:
                    # Return type mismatch
                    panic('Return type mismatch')
            else:
                # Already implemented function
                panic('Multiple function implementation')
    function_node = ASTNode('FUNCTION', _id)
    type_node_val = type_node.value
    for i in range(deref_depth):
        type_node_val = '*' + type_node_val
    type_node.value = type_node_val
    function_node.append_child(type_node)
    function_node.append_child(id_node)
    function_node.append_child(param_list_node)
    function_node.append_child(body_node)
    function_node.append_child(return_node)
    p[0] = function_node


def p_function_head(p):
    """
    function_head : type return_term
            | VOID void_id
    """
    global symbol_table_stack
    _type = p[1]
    id_node, _id, deref_depth = p[2]
    symbol_table_stack.append(SymbolTable(_type, deref_depth))
    type_node = ASTNode('TYPE', _type)
    p[0] = type_node, id_node, _id, _type, deref_depth


def p_void_id(p):
    """
    void_id : ID
            | MAIN
    """
    p[0] = ASTNode('VAR', p[1]), p[1], 0


def p_return_term(p):
    """
    return_term : function_term_r
    """
    p[0] = p[1]


def p_param_list(p):
    """
    param_list : param_list_non_empty
                |
    """
    # p[0] = ast_node
    global symbol_table_stack
    if len(p) == 2:
        param_list_ast_node, param_meta_data_list = p[1]
        current_symbol_table = symbol_table_stack[-1]
        # Add params in function symbol table
        for param_index, param in enumerate(param_meta_data_list):
            _id, _type, deref_depth = param
            if not current_symbol_table.symbol_exists(_id):
                symbol = Symbol(_id, _type, Symbol.PARAM_SCOPE, deref_depth, 4, param_index=param_index)
                param_index += 1
                current_symbol_table.add_symbol(symbol)
            else:
                panic('Param with symbol %s already declared' % _id)
        p[0] = param_list_ast_node
    elif len(p) == 1:
        p[0] = ASTNode('PARAM_LIST', 'param_list')


def p_param_list_non_empty(p):
    """
    param_list_non_empty : type function_term_r COMMA param_list_non_empty
            | type function_term_r
    """
    # p[0] = ast_node, [(id, type, deref_depth) ...]
    if len(p) == 3:
        _type = p[1]
        param_ast_node, _id, deref_depth = p[2]
        node = ASTNode('PARAM_LIST', 'param_list')
        type_child = ASTNode('TYPE', _type)
        node.prepend_child(param_ast_node)
        node.prepend_child(type_child)
        p[0] = node, [(_id, _type, deref_depth)]
    elif len(p) == 5:
        _type = p[1]
        param_ast_node, _id, deref_depth = p[2]
        param_list_ast_node, param_meta_data_list = p[4]
        type_child = ASTNode('TYPE', _type)
        param_list_ast_node.prepend_child(param_ast_node)
        param_list_ast_node.prepend_child(type_child)
        p[0] = param_list_ast_node, [(_id, _type, deref_depth)] + param_meta_data_list


# def p_function_term(p):
#     """
#     function_term : ASTERISK function_term_r
#     """
#     # p[0] = ast_node, id, deref_depth
#     child_ast_node, _id, deref_depth = p[2]
#     node = ASTNode('DEREF', '*%s' % child_ast_node.value)
#     node.append_child(child_ast_node)
#     p[0] = node, _id, deref_depth + 1


def p_function_term_r(p):
    """
    function_term_r : ASTERISK function_term_r
                        | ID
    """
    # p[0] = ast_node, id, deref_depth
    if len(p) == 2:
        _id = p[1]
        p[0] = ASTNode('VAR', _id), _id, 0
    elif len(p) == 3:
        child_ast_node, _id, deref_depth = p[2]
        node = ASTNode('DEREF', '*%s' % child_ast_node.value)
        node.append_child(child_ast_node)
        p[0] = node, _id, deref_depth + 1


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
        body.prepend_child(p[1])
    elif len(p) == 4:
        body = p[3]
        if p[1] is not None:
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
            node.append_child(p[1])
            node.append_child(p[3])
            p[0] = node
        elif p[2] == '||':
            node = ASTNode('OR', '||', p[1].is_constant and p[3].is_constant)
            node.append_child(p[1])
            node.append_child(p[3])
            p[0] = node
        elif p[1] == '(' and p[3] == ')':
            p[0] = p[2]
    elif len(p) == 3:
        node = ASTNode('NOT', '!', p[2][0].is_constant)
        node.append_child(p[2][0])
        p[0] = node
    elif len(p) == 2:
        p[0] = p[1][0]


def p_condition(p):
    """
    condition : expression EE expression
                | expression NE expression
                | expression GE expression
                | expression GT expression
                | expression LE expression
                | expression LT expression
    """
    left_ast_node, left_type, left_deref_depth = p[1]
    right_ast_node, right_type, right_deref_depth = p[3]
    if left_type != right_type or left_deref_depth != right_deref_depth:
        panic('Type mismatch at boolean operator %s' % p[2])
    if left_deref_depth != 0:
        panic('Pointer Comparision is not allowed')
    if p[2] == '==':
        node = ASTNode('EQ', '==', left_ast_node.is_constant and right_ast_node.is_constant)
        node.append_child(left_ast_node)
        node.append_child(right_ast_node)
        p[0] = node, left_type, left_deref_depth
    elif p[2] == '!=':
        node = ASTNode('NE', '!=', left_ast_node.is_constant and right_ast_node.is_constant)
        node.append_child(left_ast_node)
        node.append_child(right_ast_node)
        p[0] = node, left_type, left_deref_depth
    elif p[2] == '>=':
        node = ASTNode('GE', '>=', left_ast_node.is_constant and right_ast_node.is_constant)
        node.append_child(left_ast_node)
        node.append_child(right_ast_node)
        p[0] = node, left_type, left_deref_depth
    elif p[2] == '>':
        node = ASTNode('GT', '>', left_ast_node.is_constant and right_ast_node.is_constant)
        node.append_child(left_ast_node)
        node.append_child(right_ast_node)
        p[0] = node, left_type, left_deref_depth
    elif p[2] == '<=':
        node = ASTNode('LE', '<=', left_ast_node.is_constant and right_ast_node.is_constant)
        node.append_child(left_ast_node)
        node.append_child(right_ast_node)
        p[0] = node, left_type, left_deref_depth
    elif p[2] == '<':
        node = ASTNode('LT', '<', left_ast_node.is_constant and right_ast_node.is_constant)
        node.append_child(left_ast_node)
        node.append_child(right_ast_node)
        p[0] = node, left_type, left_deref_depth


# -------------------------------- WHILE BLOCK --------------------------------
def p_while_block(p):
    """
    while_block : WHILE L_PAREN compound_condition R_PAREN if_else_while_common_body
    """
    while_block = ASTNode('WHILE', 'while')
    while_block.append_child(p[3])
    while_block.append_child(p[5])
    p[0] = while_block


# -------------------------------- IF BLOCK --------------------------------
def p_if_block(p):
    """
    if_block : IF L_PAREN compound_condition R_PAREN if_else_while_common_body
                | IF L_PAREN compound_condition R_PAREN if_else_while_common_body ELSE if_block
                | IF L_PAREN compound_condition R_PAREN if_else_while_common_body ELSE if_else_while_common_body
    """
    if_block = ASTNode('IF', 'if')
    if_block.append_child(p[3])
    if_block.append_child(p[5])
    if len(p) == 8:
        if_block.append_child(p[7])
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
        body.append_child(p[1])
        p[0] = body
    elif len(p) == 4:
        p[0] = p[2]


# -------------------------------- STATEMENT --------------------------------
def p_statement(p):
    """
    statement : type dlist
                | assignment
    """
    global symbol_table_stack
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        dlist = p[2]
        current_symbol_table = symbol_table_stack[-1]
        _type = p[1]
        for term in dlist:
            _id, deref_depth = term
            if not current_symbol_table.symbol_exists(_id):
                symbol = Symbol(_id, _type, Symbol.LOCAL_SCOPE, deref_depth, 4)
                current_symbol_table.add_symbol(symbol)
            else:
                panic('Symbol already declared %s' % _id)


def p_statement_func_expr(p):
    """
    statement : func_expr
    """
    node, _, _ = p[1]
    p[0] = node


# -------------------------------- DECLARATION --------------------------------
def p_type(p):
    """
    type : INT
        | FLOAT
    """
    p[0] = p[1]


def p_dlist(p):
    """
    dlist : declaration COMMA dlist
            | declaration
    """
    # p[0] = [(id, deref_depth), ...]
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 4:
        p[0] = [p[1]] + p[3]


def p_declaration(p):
    """
    declaration : ID
                | ASTERISK declaration %prec DE_REF
    """
    # p[0] = id, deref_depth
    if len(p) == 2:
        p[0] = p[1], 0
    elif len(p) == 3:
        p[0] = p[2][0], p[2][1] + 1


# -------------------------------- RETURN STATEMENT ----------------------------
def p_return_statement(p):
    """
    return_statement : RETURN expression SEMICOLON
                | RETURN SEMICOLON
                |
    """
    global symbol_table_stack, global_symbol_table
    fun = symbol_table_stack[-1]
    fun_type = fun.type
    fun_deref_depth = fun.deref_depth
    if len(p) == 4:
        ast_node, _type, deref_depth = p[2]
        if fun_type != _type or fun_deref_depth != deref_depth:
            panic('Improper return type in function implementation')
        node = ASTNode('RETURN', 'return')
        node.append_child(ast_node)
        p[0] = node, True
    elif len(p) == 3 or len(p) == 1:
        if fun_type != 'void':
            panic('Improper return type in function implementation')
        node = ASTNode('RETURN', 'return')
        if len(p) == 3:
            p[0] = node, True
        elif len(p) == 1:
            p[0] = node, False


# -------------------------------- ASSIGNMENT --------------------------------
def p_assignment(p):
    """
    assignment :  ID EQUALS expression
                | ASTERISK term EQUALS expression %prec DE_REF
    """
    global no_assignments
    no_assignments += 1
    global global_symbol_table, symbol_table_stack
    if len(p) == 4:
        # ID = expr
        expr_ast_node, expr_type, expr_deref_depth = p[3]
        if expr_ast_node.is_constant:
            panic('Constant cannot be assigned directly without de-referencing')
        _id = p[1]
        lhs_symbol = None
        try:
            lhs_symbol = get_non_func_symbol_from_stack(_id, global_symbol_table, symbol_table_stack)
        except KeyError:
            panic('Symbol %s accessed without declaration' % _id)
        if lhs_symbol.deref_depth == 0:
            panic('Scalar %s cannot be directly assigned' % _id)
        if lhs_symbol.type != expr_type or lhs_symbol.deref_depth != expr_deref_depth:
            panic('Type mismatch while assigning %s' % _id)
        id_node = ASTNode('VAR', _id)
        node = ASTNode('ASGN', '=')
        node.append_child(id_node)
        node.append_child(expr_ast_node)
        p[0] = node
    elif len(p) == 5:
        term_node, term_type, term_deref_depth = p[2]
        expr_ast_node, expr_type, expr_deref_depth = p[4]
        if term_deref_depth <= 0:
            panic('Symbol de-referenced too many times')
        if term_type != expr_type or term_deref_depth - 1 != expr_deref_depth:
            panic('Type mismatch at assignment')
        asterisk_node = ASTNode('DEREF', '*%s' % term_node.value)
        asterisk_node.append_child(term_node)
        node = ASTNode('ASGN', '=')
        node.append_child(asterisk_node)
        node.append_child(expr_ast_node)
        p[0] = node


# -------------------------------- EXPRESSION --------------------------------
def p_expression_function_call(p):
    """
    expression : func_expr
    """
    p[0] = p[1]


def p_func_expr(p):
    """
    func_expr : ID L_PAREN arg_list R_PAREN
    """
    if len(p) == 5:
        _id = p[1]
        func_symbol = None
        arg_list_ast_node, arg_types = p[3]
        if global_symbol_table.symbol_exists(_id):
            func_symbol = global_symbol_table.get_symbol(_id)
            if func_symbol.is_function():
                param_list = func_symbol.its_table.get_param_signature()
                if param_list != arg_types:
                    panic('Function %s arguments are mismatched' % _id)
            else:
                panic('Symbol %s is not a function' % _id)
        else:
            panic('Function called without declaration %s' % _id)
        node = ASTNode('FUNCTION_CALL', 'function_call')
        id_node = ASTNode('VAR', p[1])
        node.append_child(id_node)
        node.append_child(arg_list_ast_node)
        p[0] = node, func_symbol.type, func_symbol.deref_depth


def p_arg_list(p):
    """
    arg_list : arg_list_non_empty
            |
    """
    # p[0] := ast_node, [(type, deref_depth, arg_index), ...]
    if len(p) == 1:
        node = ASTNode('ARG_LIST', 'arg_list')
        p[0] = node, []
    elif len(p) == 2:
        p[0] = p[1]


def p_arg_list_non_empty(p):
    """
    arg_list_non_empty : arg_list_non_empty COMMA expression
                    | expression
    """
    # p[0] := ast_node, [(type, deref_depth, arg_index), ...]
    if len(p) == 2:
        expr_ast_node, _type, deref_depth = p[1]
        node = ASTNode('ARG_LIST', 'arg_list')
        node.append_child(expr_ast_node)
        arg_list = [(_type, deref_depth, 0)]
        p[0] = node, arg_list
    elif len(p) == 4:
        node, arg_list = p[1]
        expr_ast_node, _type, deref_depth = p[3]
        node.append_child(expr_ast_node)
        current_arg = [(_type, deref_depth, len(arg_list))]
        arg_list = arg_list + current_arg
        p[0] = node, arg_list


def p_expression_binary_op(p):
    """
    expression : expression PLUS expression
              | expression MINUS expression
              | expression ASTERISK expression
              | expression DIVIDE expression
    """
    left_child_node, left_type, left_deref_depth = p[1]
    right_child_node, right_type, right_deref_depth = p[3]
    if left_type != right_type or left_deref_depth != right_deref_depth:
        panic('Type mismatch for operation %s' % p[2])
    if left_deref_depth != 0:
        panic('Pointer Arthmatic is not allowed')
    if p[2] == '+':
        node = ASTNode('PLUS', '+', left_child_node.is_constant and right_child_node.is_constant)
        node.append_child(left_child_node)
        node.append_child(right_child_node)
        p[0] = node, left_type, left_deref_depth
    elif p[2] == '-':
        node = ASTNode('MINUS', '-', left_child_node.is_constant and right_child_node.is_constant)
        node.append_child(left_child_node)
        node.append_child(right_child_node)
        p[0] = node, left_type, left_deref_depth
    elif p[2] == '*':
        node = ASTNode('MUL', '*', left_child_node.is_constant and right_child_node.is_constant)
        node.append_child(left_child_node)
        node.append_child(right_child_node)
        p[0] = node, left_type, left_deref_depth
    elif p[2] == '/':
        node = ASTNode('DIV', '/', left_child_node.is_constant and right_child_node.is_constant)
        node.append_child(left_child_node)
        node.append_child(right_child_node)
        p[0] = node, left_type, left_deref_depth


def p_expression_uminus(p):
    """expression : MINUS expression %prec U_MINUS"""
    child_ast_node, _type, deref_depth = p[2]
    node = ASTNode('UMINUS', '-', child_ast_node.is_constant)
    node.append_child(child_ast_node)
    p[0] = node, _type, deref_depth


def p_expression_group(p):
    """expression : L_PAREN expression R_PAREN"""
    p[0] = p[2]


def p_expression_int_lit(p):
    """expression : INT_LIT"""
    p[0] = ASTNode('CONST', p[1], True), 'int', 0


def p_expression_float_lit(p):
    """expression : FLOAT_LIT"""
    p[0] = ASTNode('CONST', p[1], True), 'float', 0


def p_expression_term(p):
    """expression : term"""
    term_ast_node, _type, deref_depth = p[1]
    if term_ast_node.type == 'VAR' and deref_depth == 0:
        panic('Direct use of non pointer variable')
    p[0] = p[1]


# -------------------------------- TERM --------------------------------
def p_term(p):
    """
    term : ASTERISK term %prec DE_REF
        | AMPERSAND ID %prec ADDR_OF
        | ID

    """
    global global_symbol_table, symbol_table_stack
    if len(p) == 2:
        try:
            _id = p[1]
            sym = get_non_func_symbol_from_stack(_id, global_symbol_table, symbol_table_stack)
            p[0] = ASTNode('VAR', _id), sym.type, sym.deref_depth
        except KeyError:
            panic('Symbol accessed without declaration')
    elif len(p) == 3:
        if p[1] == '*':
            child_ast_node, _type, deref_depth = p[2]
            if deref_depth == 0:
                panic('Symbol de-referenced too many times')
            node = ASTNode('DEREF', '*%s' % child_ast_node.value)
            node.append_child(child_ast_node)
            p[0] = node, _type, deref_depth - 1
        elif p[1] == '&':
            try:
                _id = p[2]
                sym = get_non_func_symbol_from_stack(_id, global_symbol_table, symbol_table_stack)
                node = ASTNode('ADDR', '&%s' % _id)
                id_node = ASTNode('VAR', _id)
                node.append_child(id_node)
                p[0] = node, sym.type, sym.deref_depth + 1
            except KeyError:
                panic('Symbol accessed without declaration')


# -------------------------------- ERROR --------------------------------
def panic(message):
    print(message)
    exit(-1)


def p_error(p):
    if p:
        print('syntax error at {0} in line {1}'.format(p.value, p.lineno))
    else:
        print('syntax error at EOF')


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
