registers_available = [1, 1, 1, 1, 1, 1, 1, 1]


def get_available_register():
    global registers_available
    index = registers_available.index(1)
    registers_available[index] = 0
    return index


def free_register(index):
    global registers_available
    registers_available[index] = 1


def generate_assembly_code_for_binary_op(operator, op1, op2):
    cur_index = get_available_register()
    assembly_code = ''
    if operator == '+':
        assembly_code += '\t'
        assembly_code += 'add $s%d, $s%d, $s%d\n' % (cur_index, op1, op2)
        free_register(op1)
        free_register(op2)
    elif operator == '-':
        assembly_code += '\t'
        assembly_code += 'sub $s%d, $s%d, $s%d\n' % (cur_index, op1, op2)
        free_register(op1)
        free_register(op2)
    elif operator == '*':
        assembly_code += '\t'
        assembly_code += 'mul $s%d, $s%d, $s%d\n' % (cur_index, op1, op2)
        free_register(op1)
        free_register(op2)
    elif operator == '/':
        assembly_code += '\t'
        assembly_code += 'div $s%d, $s%d\n\tmflo $s%d\n' % (op1, op2, cur_index)
        free_register(op1)
        free_register(op2)
    elif operator == '==':
        assembly_code += '\t'
        assembly_code += 'seq $s%d, $s%d, $s%d\n' % (cur_index, op1, op2)
        free_register(op1)
        free_register(op2)
    elif operator == '!=':
        assembly_code += '\t'
        assembly_code += 'sne $s%d, $s%d, $s%d\n' % (cur_index, op1, op2)
        free_register(op1)
        free_register(op2)
    elif operator == '<':
        assembly_code += '\t'
        assembly_code += 'slt $s%d, $s%d, $s%d\n' % (cur_index, op1, op2)
        free_register(op1)
        free_register(op2)
    elif operator == '>':
        assembly_code += '\t'
        assembly_code += 'slt $s%d, $s%d, $s%d\n' % (cur_index, op2, op1)
        free_register(op1)
        free_register(op2)
    elif operator == '<=':
        assembly_code += '\t'
        assembly_code += 'slt $s%d, $s%d, $s%d\n' % (cur_index, op2, op1)
        free_register(op1)
        free_register(op2)
        temp_index = get_available_register()
        assembly_code += '\t'
        assembly_code += 'not $s%d, $s%d\n' % (temp_index, cur_index)
        free_register(cur_index)
        cur_index = temp_index
    elif operator == '>=':
        assembly_code += '\t'
        assembly_code += 'slt $s%d, $s%d, $s%d\n' % (cur_index, op1, op2)
        free_register(op1)
        free_register(op2)
        temp_index = get_available_register()
        assembly_code += '\t'
        assembly_code += 'not $s%d, $s%d\n' % (temp_index, cur_index)
        free_register(cur_index)
        cur_index = temp_index
    elif operator == '||':
        assembly_code += '\t'
        assembly_code += 'or $s%d, $s%d, $s%d\n' % (cur_index, op1, op2)
        free_register(op1)
        free_register(op2)
    elif operator == '&&':
        assembly_code += '\t'
        assembly_code += 'and $s%d, $s%d, $s%d\n' % (cur_index, op1, op2)
        free_register(op1)
        free_register(op2)
    this_index = get_available_register()
    assembly_code += '\t'
    assembly_code += 'move $s%d, $s%d\n' % (this_index, cur_index)
    free_register(cur_index)
    return this_index, assembly_code


def generate_assembly_code_for_unary_op(operator, op1):
    cur_index = get_available_register()
    assembly_code = ''
    if operator == '-':
        assembly_code += '\t'
        assembly_code += 'negu $s%d, $s%d\n' % (cur_index, op1)
    elif operator == '!':
        assembly_code += '\t'
        assembly_code += 'not $s%d, $s%d\n' % (cur_index, op1)
    free_register(op1)
    this_index = get_available_register()
    assembly_code += '\t'
    assembly_code += 'move $s%d, $s%d\n' % (this_index, cur_index)
    free_register(cur_index)
    return this_index, assembly_code


def generate_register_for_rhs_term(astnode, symbol_table, global_symbol_table):
    assembly_code = ''
    if astnode.type == 'CONST':
        index = get_available_register()
        assembly_code += '\t'
        assembly_code += 'li $s%d, %s\n' % (index, astnode.value)
        return index, assembly_code
    elif astnode.type == 'VAR':
        index = get_available_register()
        _id = astnode.value
        if symbol_table.symbol_exists(_id):
            offset = symbol_table.get_symbol(_id).offset
            assembly_code += '\t'
            assembly_code += 'lw $s%d, %d($sp)\n' % (index, offset)
            return index, assembly_code
        elif global_symbol_table.symbol_exists(_id):
            assembly_code += '\t'
            assembly_code += 'lw $s%d, global_%s\n' % (index, _id)
            return index, assembly_code
    elif astnode.type == 'DEREF':
        child_index, child_assembly_code = generate_register_for_rhs_term(astnode.children[0], symbol_table,
                                                                          global_symbol_table)
        index = get_available_register()
        assembly_code += '\t'
        assembly_code += 'lw $s%d, 0($s%d)\n' % (index, child_index)
        free_register(child_index)
        return index, child_assembly_code + assembly_code
    elif astnode.type == 'ADDR':
        index = get_available_register()
        _id = astnode.children[0].value
        if symbol_table.symbol_exists(_id):
            offset = symbol_table.get_symbol(_id).offset
            assembly_code += '\t'
            assembly_code += 'addi $s%d, $sp, %d\n' % (index, offset)
            return index, assembly_code
        elif global_symbol_table.symbol_exists(_id):
            assembly_code += '\t'
            assembly_code += 'la $s%d, global_%s\n' % (index, _id)
            return index, assembly_code


def generate_register_for_lhs_term(astnode, symbol_table, global_symbol_table):
    if astnode.type == 'DEREF':
        index, assembly_code = generate_register_for_rhs_term(astnode.children[0], symbol_table, global_symbol_table)
        return index, assembly_code


def generate_assembly_code_for_expression(astnode, symbol_table, global_symbol_table):
    if astnode.is_term():
        index, assembly_code = generate_register_for_rhs_term(astnode, symbol_table, global_symbol_table)
        return index, assembly_code
    else:
        if len(astnode.children) == 2:
            lhs = astnode.children[0]
            rhs = astnode.children[1]
            lhs_index, lhs_assembly_code = generate_assembly_code_for_expression(lhs, symbol_table, global_symbol_table)
            rhs_index, rhs_assembly_code = generate_assembly_code_for_expression(rhs, symbol_table, global_symbol_table)
            this_index, this_assembly_code = generate_assembly_code_for_binary_op(astnode.value, lhs_index, rhs_index)
            return this_index, lhs_assembly_code + rhs_assembly_code + this_assembly_code
        elif len(astnode.children) == 1:
            child = astnode.children[0]
            child_index, child_assembly_code = generate_assembly_code_for_expression(child, symbol_table,
                                                                                     global_symbol_table)
            this_index, this_assembly_code = generate_assembly_code_for_unary_op(astnode.value, child_index)
            return this_index, child_assembly_code + this_assembly_code


def generate_assembly_code_for_assignment(astnode, symbol_table, global_symbol_table):
    if astnode.type == 'ASGN':
        lhs = astnode.children[0]
        rhs = astnode.children[1]
        this_assembly_code = ''
        rhs_index, rhs_assembly_code = generate_assembly_code_for_expression(rhs, symbol_table, global_symbol_table)
        if lhs.type == 'DEREF':
            lhs_index, lhs_assembly_code = generate_register_for_lhs_term(lhs, symbol_table, global_symbol_table)
            this_assembly_code += '\t'
            this_assembly_code += 'sw $s%d, 0($s%d)\n' % (rhs_index, lhs_index)
            free_register(lhs_index)
            free_register(rhs_index)
            return rhs_assembly_code + lhs_assembly_code + this_assembly_code
        elif lhs.type == 'VAR':
            _id = lhs.value
            if symbol_table.symbol_exists(_id):
                offset = symbol_table.get_symbol(_id).offset
                this_assembly_code += '\t'
                this_assembly_code += 'sw $s%d, %d($sp)\n' % (rhs_index, offset)
                free_register(rhs_index)
                return rhs_assembly_code + this_assembly_code
            elif global_symbol_table.symbol_exists(_id):
                this_assembly_code += '\t'
                this_assembly_code += 'sw $s%d, global_%s\n' % (rhs_index, _id)
                free_register(rhs_index)
                return rhs_assembly_code + this_assembly_code

    else:
        print('Wrong fn call')
        return ''


def generate_assembly_code_for_fn(cfgnode, symbol_table, global_symbol_table, fn_name=None):
    txt = ''
    if cfgnode.type == 'ASGN_BLOCK':
        txt += 'label%d:\n' % cfgnode.block_number
        for child in cfgnode.value:
            # Assignment
            asgn = child
            if asgn.type == 'ASGN':
                txt += generate_assembly_code_for_assignment(asgn, symbol_table, global_symbol_table)
        goto = cfgnode.goto_block_number()
        txt += '\t'
        txt += 'j label%d\n' % goto

    elif cfgnode.type == 'CONDITION_BLOCK':
        txt += 'label%d:\n' % cfgnode.block_number
        cond_index, cond_assembly_code = generate_assembly_code_for_expression(cfgnode.value, symbol_table,
                                                                               global_symbol_table)
        goto_true, goto_false = cfgnode.goto_block_number()
        txt += cond_assembly_code
        txt += '\t'
        txt += 'bne $s%d, $0, label%d\n' % (cond_index, goto_true)
        txt += '\t'
        txt += 'j label%d\n' % goto_false
        free_register(cond_index)

    elif cfgnode.type == 'RETURN_BLOCK':
        txt += 'label%d:\n' % cfgnode.block_number
        return_node = cfgnode.children[0]
        return_node_list = return_node.children
        if len(return_node_list) == 1:
            return_node_val = return_node_list[0]
            return_index, return_assembly_code = generate_assembly_code_for_expression(return_node_val, symbol_table,
                                                                                       global_symbol_table)
            txt += return_assembly_code
            txt += '\t'
            txt += 'move $v1, $s%d # move return value to $v1\n' % return_index
            txt += '\t'
            txt += 'j epilogue_%s\n' % fn_name
            free_register(return_index)
        else:
            txt += '\t'
            txt += 'j epilogue_%s\n' % fn_name

    elif cfgnode.type == 'FUNCTION_BLOCK':
        symbol_table.reset_offsets()
        body_cfg_node, return_cfg_node = cfgnode.children
        txt = '\t.text\t# The .text assembler directive indicates\n\t.globl %s\t# The following is the code\n' % fn_name
        txt += '%s:\n' % fn_name
        txt += '# Prologue begins\n'
        txt += '\tsw $ra, 0($sp)\t# Save the return address\n'
        txt += '\tsw $fp, -4($sp)\t# Save the frame pointer\n'
        txt += '\tsub $fp, $sp, 8\t# Update the frame pointer\n'
        txt += '\tsub $sp, $sp, %d\t# Make space for the locals\n' % (symbol_table.local_sym_cumulative_width + 8)
        txt += '# Prologue ends\n'
        txt += generate_assembly_code_for_fn(body_cfg_node, symbol_table, global_symbol_table)
        txt += generate_assembly_code_for_fn(return_cfg_node, symbol_table, global_symbol_table, fn_name=fn_name)
        txt += '\n'
        txt += '# Epilogue begins\n'
        txt += 'epilogue_%s:\n' % fn_name
        txt += '\tadd $sp, $sp, %d\n' % (symbol_table.local_sym_cumulative_width + 8)
        txt += '\tlw $fp, -4($sp)\n'
        txt += '\tlw $ra, 0($sp)\n'
        txt += '\tjr $ra\t# Jump back to the called procedure\n'
        txt += '# Epilogue ends\n'

    else:
        txt = ''
        for child in cfgnode.children:
            txt += generate_assembly_code_for_fn(child, symbol_table, global_symbol_table)

    return txt


def generate_assembly_code_for_globals(global_sym_table):
    txt = '\t.data\n'
    sorted_globals_list = []
    for _id, global_sym in global_sym_table.symbols.items():
        if not global_sym.is_function():
            sorted_globals_list.append((_id, global_sym))

    sorted_globals_list.sort(key=lambda p: p[0])

    for id_sym_tuple in sorted_globals_list:
        _id = id_sym_tuple[0]
        sym = id_sym_tuple[1]
        if sym.type == 'float' and sym.deref_depth == 0:
            txt += 'global_%s:\t.space\t8\n' % _id
        else:
            txt += 'global_%s:\t.word\t0\n' % _id

    return txt
