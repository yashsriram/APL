registers_available = [1, 1, 1, 1, 1, 1, 1, 1]
float_registers_available = [1, 1, 1, 1, 1, 1, 1, 1]
float_cmp_label = 0


def get_available_register():
    global registers_available
    index = registers_available.index(1)
    registers_available[index] = 0
    return index


def free_register(index):
    global registers_available
    registers_available[index] = 1


def get_available_float_register():
    global float_registers_available
    index = float_registers_available.index(1)
    float_registers_available[index] = 0
    return index


def free_float_register(index):
    global float_registers_available
    float_registers_available[index] = 1


def get_next_float_cmp_label():
    global float_cmp_label
    ans = float_cmp_label
    float_cmp_label += 1
    return ans


def generate_assembly_code_for_binary_op(operator, op1, op2, op_type):
    assembly_code = ''
    ret_type = None
    cur_index = None
    if operator == '+':
        assembly_code += '\t'
        if op_type == 'int':
            cur_index = get_available_register()
            assembly_code += 'add $s%d, $s%d, $s%d\n' % (cur_index, op1, op2)
            free_register(op1)
            free_register(op2)
        elif op_type == 'float':
            cur_index = get_available_float_register()
            assembly_code += 'add.s $f%d, $f%d, $f%d\n' % (10 + 2 * cur_index, 10 + 2 * op1, 10 + 2 * op2)
            free_float_register(op1)
            free_float_register(op2)
        ret_type = op_type
    elif operator == '-':
        assembly_code += '\t'
        if op_type == 'int':
            cur_index = get_available_register()
            assembly_code += 'sub $s%d, $s%d, $s%d\n' % (cur_index, op1, op2)
            free_register(op1)
            free_register(op2)
        elif op_type == 'float':
            cur_index = get_available_float_register()
            assembly_code += 'sub.s $f%d, $f%d, $f%d\n' % (10 + 2 * cur_index, 10 + 2 * op1, 10 + 2 * op2)
            free_float_register(op1)
            free_float_register(op2)
        ret_type = op_type
    elif operator == '*':
        assembly_code += '\t'
        if op_type == 'int':
            cur_index = get_available_register()
            assembly_code += 'mul $s%d, $s%d, $s%d\n' % (cur_index, op1, op2)
            free_register(op1)
            free_register(op2)
        elif op_type == 'float':
            cur_index = get_available_float_register()
            assembly_code += 'mul.s $f%d, $f%d, $f%d\n' % (10 + 2 * cur_index, 10 + 2 * op1, 10 + 2 * op2)
            free_float_register(op1)
            free_float_register(op2)
        ret_type = op_type
    elif operator == '/':
        assembly_code += '\t'
        if op_type == 'int':
            cur_index = get_available_register()
            assembly_code += 'div $s%d, $s%d\n\tmflo $s%d\n' % (op1, op2, cur_index)
            free_register(op1)
            free_register(op2)
        elif op_type == 'float':
            cur_index = get_available_float_register()
            assembly_code += 'div.s $f%d, $f%d, $f%d\n' % (10 + 2 * cur_index, 10 + 2 * op1, 10 + 2 * op2)
            free_float_register(op1)
            free_float_register(op2)
        ret_type = op_type
    elif operator == '==':
        assembly_code += '\t'
        cur_index = get_available_register()
        if op_type == 'int':
            assembly_code += 'seq $s%d, $s%d, $s%d\n' % (cur_index, op1, op2)
            free_register(op1)
            free_register(op2)
        elif op_type == 'float':
            assembly_code += 'c.eq.s $f%d, $f%d\n' % (10 + 2 * op1, 10 + 2 * op2)
            label_val = get_next_float_cmp_label()
            assembly_code += '\tbc1f L_CondFalse_%d\n' % label_val
            assembly_code += '\tli $s%d, 1\n' % cur_index
            assembly_code += '\tj L_CondEnd_%d\n' % label_val
            assembly_code += 'L_CondFalse_%d:\n' % label_val
            assembly_code += '\tli $s%d, 0\n' % cur_index
            assembly_code += 'L_CondEnd_%d:\n' % label_val
            free_float_register(op1)
            free_float_register(op2)
        ret_type = 'int'
    elif operator == '!=':
        assembly_code += '\t'
        cur_index = get_available_register()
        if op_type == 'int':
            assembly_code += 'sne $s%d, $s%d, $s%d\n' % (cur_index, op1, op2)
            free_register(op1)
            free_register(op2)
        elif op_type == 'float':
            assembly_code += 'c.eq.s $f%d, $f%d\n' % (10 + 2 * op1, 10 + 2 * op2)
            label_val = get_next_float_cmp_label()
            assembly_code += '\tbc1f L_CondTrue_%d\n' % label_val
            assembly_code += '\tli $s%d, 0\n' % cur_index
            assembly_code += '\tj L_CondEnd_%d\n' % label_val
            assembly_code += 'L_CondTrue_%d:\n' % label_val
            assembly_code += '\tli $s%d, 1\n' % cur_index
            assembly_code += 'L_CondEnd_%d:\n' % label_val
            free_float_register(op1)
            free_float_register(op2)
        ret_type = 'int'
    elif operator == '<':
        assembly_code += '\t'
        cur_index = get_available_register()
        if op_type == 'int':
            assembly_code += 'slt $s%d, $s%d, $s%d\n' % (cur_index, op1, op2)
            free_register(op1)
            free_register(op2)
        elif op_type == 'float':
            assembly_code += 'c.lt.s $f%d, $f%d\n' % (10 + 2 * op1, 10 + 2 * op2)
            label_val = get_next_float_cmp_label()
            assembly_code += '\tbc1f L_CondFalse_%d\n' % (label_val)
            assembly_code += '\tli $s%d, 1\n' % (cur_index)
            assembly_code += '\tj L_CondEnd_%d\n' % (label_val)
            assembly_code += 'L_CondFalse_%d:\n' % (label_val)
            assembly_code += '\tli $s%d, 0\n' % (cur_index)
            assembly_code += 'L_CondEnd_%d:\n' % (label_val)
            free_float_register(op1)
            free_float_register(op2)
        ret_type = 'int'
    elif operator == '>':
        assembly_code += '\t'
        cur_index = get_available_register()
        if op_type == 'int':
            assembly_code += 'slt $s%d, $s%d, $s%d\n' % (cur_index, op2, op1)
            free_register(op1)
            free_register(op2)
        elif op_type == 'float':
            assembly_code += 'c.lt.s $f%d, $f%d\n' % (10 + 2 * op2, 10 + 2 * op1)
            label_val = get_next_float_cmp_label()
            assembly_code += '\tbc1f L_CondFalse_%d\n' % (label_val)
            assembly_code += '\tli $s%d, 1\n' % (cur_index)
            assembly_code += '\tj L_CondEnd_%d\n' % (label_val)
            assembly_code += 'L_CondFalse_%d:\n' % (label_val)
            assembly_code += '\tli $s%d, 0\n' % (cur_index)
            assembly_code += 'L_CondEnd_%d:\n' % (label_val)
            free_float_register(op1)
            free_float_register(op2)
        ret_type = 'int'
    elif operator == '<=':
        assembly_code += '\t'
        cur_index = get_available_register()
        if op_type == 'int':
            assembly_code += 'slt $s%d, $s%d, $s%d\n' % (cur_index, op2, op1)
            free_register(op1)
            free_register(op2)
            temp_index = get_available_register()
            assembly_code += '\t'
            assembly_code += 'xori $s%d, $s%d, 1\n' % (temp_index, cur_index)
            free_register(cur_index)
            cur_index = temp_index
        elif op_type == 'float':
            assembly_code += 'c.le.s $f%d, $f%d\n' % (10 + 2 * op1, 10 + 2 * op2)
            label_val = get_next_float_cmp_label()
            assembly_code += '\tbc1f L_CondFalse_%d\n' % (label_val)
            assembly_code += '\tli $s%d, 1\n' % (cur_index)
            assembly_code += '\tj L_CondEnd_%d\n' % (label_val)
            assembly_code += 'L_CondFalse_%d:\n' % (label_val)
            assembly_code += '\tli $s%d, 0\n' % (cur_index)
            assembly_code += 'L_CondEnd_%d:\n' % (label_val)
            free_float_register(op1)
            free_float_register(op2)
        ret_type = 'int'
    elif operator == '>=':
        assembly_code += '\t'
        cur_index = get_available_register()
        if op_type == 'int':
            assembly_code += 'slt $s%d, $s%d, $s%d\n' % (cur_index, op1, op2)
            free_register(op1)
            free_register(op2)
            temp_index = get_available_register()
            assembly_code += '\t'
            assembly_code += 'xori $s%d, $s%d, 1\n' % (temp_index, cur_index)
            free_register(cur_index)
            cur_index = temp_index
        elif op_type == 'float':
            assembly_code += 'c.le.s $f%d, $f%d\n' % (10 + 2 * op2, 10 + 2 * op1)
            label_val = get_next_float_cmp_label()
            assembly_code += '\tbc1f L_CondFalse_%d\n' % (label_val)
            assembly_code += '\tli $s%d, 1\n' % (cur_index)
            assembly_code += '\tj L_CondEnd_%d\n' % (label_val)
            assembly_code += 'L_CondFalse_%d:\n' % (label_val)
            assembly_code += '\tli $s%d, 0\n' % (cur_index)
            assembly_code += 'L_CondEnd_%d:\n' % (label_val)
            free_float_register(op1)
            free_float_register(op2)
        ret_type = 'int'
    elif operator == '||':
        cur_index = get_available_register()
        assembly_code += '\t'
        assembly_code += 'or $s%d, $s%d, $s%d\n' % (cur_index, op1, op2)
        free_register(op1)
        free_register(op2)
        ret_type = 'int'
    elif operator == '&&':
        cur_index = get_available_register()
        assembly_code += '\t'
        assembly_code += 'and $s%d, $s%d, $s%d\n' % (cur_index, op1, op2)
        free_register(op1)
        free_register(op2)
        ret_type = 'int'
    this_index = None
    if ret_type == 'int':
        this_index = get_available_register()
        assembly_code += '\t'
        assembly_code += 'move $s%d, $s%d\n' % (this_index, cur_index)
        free_register(cur_index)
    elif ret_type == 'float':
        this_index = get_available_float_register()
        assembly_code += '\t'
        assembly_code += 'mov.s $f%d, $f%d\n' % (10 + 2 * this_index, 10 + 2 * cur_index)
        free_float_register(cur_index)
    return this_index, assembly_code, ret_type


def generate_assembly_code_for_unary_op(operator, op1, op_type):
    assembly_code = ''
    ret_type = None
    cur_index = None
    if operator == '-':
        assembly_code += '\t'
        if op_type == 'int':
            cur_index = get_available_register()
            assembly_code += 'negu $s%d, $s%d\n' % (cur_index, op1)
            free_register(op1)
        elif op_type == 'float':
            cur_index = get_available_float_register()
            assembly_code += 'neg.s $f%d, $f%d\n' % (10 + 2 * cur_index, 10 + 2 * op1)
            free_float_register(op1)
        ret_type = op_type
    elif operator == '!':
        cur_index = get_available_register()
        assembly_code += '\t'
        assembly_code += 'xori $s%d, $s%d, 1\n' % (cur_index, op1)
        free_register(op1)
        ret_type = 'int'
    this_index = None
    if ret_type == 'int':
        this_index = get_available_register()
        assembly_code += '\t'
        assembly_code += 'move $s%d, $s%d\n' % (this_index, cur_index)
        free_register(cur_index)
    elif ret_type == 'float':
        this_index = get_available_float_register()
        assembly_code += '\t'
        assembly_code += 'mov.s $f%d, $f%d\n' % (10 + 2 * this_index, 10 + 2 * cur_index)
        free_float_register(cur_index)
    return this_index, assembly_code, ret_type


def generate_register_for_rhs_term(astnode, symbol_table, global_symbol_table):
    assembly_code = ''
    if astnode.type == 'CONST':
        const_val = astnode.value
        if type(const_val) is int:
            index = get_available_register()
            assembly_code += '\t'
            assembly_code += 'li $s%d, %s\n' % (index, const_val)
            return index, assembly_code, 'int', 0
        elif type(const_val) is float:
            index = get_available_float_register()
            assembly_code += '\t'
            assembly_code += 'li.s $f%d, %s\n' % (10 + 2 * index, const_val)
            return index, assembly_code, 'float', 0
    elif astnode.type == 'VAR':
        _id = astnode.value
        if symbol_table.symbol_exists(_id):
            symbol = symbol_table.get_symbol(_id)
            offset = symbol.offset
            if symbol.type == 'float' and symbol.deref_depth == 0:
                index = get_available_float_register()
                assembly_code += '\t'
                assembly_code += 'l.s $f%d, %d($sp)\n' % (10 + 2 * index, offset)
            else:
                index = get_available_register()
                assembly_code += '\t'
                assembly_code += 'lw $s%d, %d($sp)\n' % (index, offset)
            return index, assembly_code, symbol.type, symbol.deref_depth
        elif global_symbol_table.symbol_exists(_id):
            symbol = global_symbol_table.get_symbol(_id)
            if symbol.type == 'float' and symbol.deref_depth == 0:
                index = get_available_float_register()
                assembly_code += '\t'
                assembly_code += 'l.s $f%d, global_%s\n' % (10 + 2 * index, _id)
            else:
                index = get_available_register()
                assembly_code += '\t'
                assembly_code += 'lw $s%d, global_%s\n' % (index, _id)
            return index, assembly_code, symbol.type, symbol.deref_depth
    elif astnode.type == 'DEREF':
        child_index, child_assembly_code, child_type, child_deref_depth = generate_register_for_rhs_term(
            astnode.children[0], symbol_table,
            global_symbol_table)
        if child_type == 'float' and child_deref_depth == 1:
            index = get_available_float_register()
            assembly_code += '\t'
            assembly_code += 'l.s $f%d, 0($s%d)\n' % (10 + 2 * index, child_index)
        else:
            index = get_available_register()
            assembly_code += '\t'
            assembly_code += 'lw $s%d, 0($s%d)\n' % (index, child_index)
        free_register(child_index)
        return index, child_assembly_code + assembly_code, child_type, child_deref_depth - 1
    elif astnode.type == 'ADDR':
        index = get_available_register()
        _id = astnode.children[0].value
        if symbol_table.symbol_exists(_id):
            symbol = symbol_table.get_symbol(_id)
            offset = symbol.offset
            assembly_code += '\t'
            assembly_code += 'addi $s%d, $sp, %d\n' % (index, offset)
            return index, assembly_code, symbol.type, symbol.deref_depth + 1
        elif global_symbol_table.symbol_exists(_id):
            symbol = global_symbol_table.get_symbol(_id)
            assembly_code += '\t'
            assembly_code += 'la $s%d, global_%s\n' % (index, _id)
            return index, assembly_code, symbol.type, symbol.deref_depth + 1


def generate_register_for_lhs_term(astnode, symbol_table, global_symbol_table):
    if astnode.type == 'DEREF':
        index, assembly_code, _type, deref_depth = generate_register_for_rhs_term(astnode.children[0], symbol_table,
                                                                                  global_symbol_table)
        return index, assembly_code, _type, deref_depth - 1


def generate_assembly_code_for_expression(astnode, symbol_table, global_symbol_table):
    if astnode.is_term():
        index, assembly_code, _type, deref_depth = generate_register_for_rhs_term(astnode, symbol_table,
                                                                                  global_symbol_table)
        return index, assembly_code, _type, deref_depth
    elif astnode.is_function_call():
        # args
        id_node, arg_list = astnode.children
        # params
        func_name = id_node.value
        func = global_symbol_table.get_symbol(func_name)
        func_params = func.its_child_table.get_params_in_order()
        # calculate offsets
        offsets = []
        offset = 0
        for i in range(len(func_params) - 1, -1, -1):
            offsets = [offset] + offsets
            offset -= func_params[i].width
        #
        assembly_code = '\t# setting up activation record for called function\n'
        for i, arg in enumerate(arg_list.children):
            index, arg_assembly_code, _type, deref_depth = generate_assembly_code_for_expression(
                arg, symbol_table, global_symbol_table)
            assembly_code += arg_assembly_code
            if _type == 'float' and deref_depth == 0:
                assembly_code += '\ts.s $f%d, %d($sp)\n' % (10 + 2 * index, offsets[i])
                free_float_register(index)
            else:
                assembly_code += '\tsw $s%d, %d($sp)\n' % (index, offsets[i])
                free_register(index)
        assembly_code += '\tsub $sp, $sp, %d\n' % -offset
        assembly_code += '\tjal %s # function call\n' % func_name
        assembly_code += '\tadd $sp, $sp, %d # destroying activation record of called function\n' % -offset
        if func.type == 'float' and func.deref_depth == 0:
            index = get_available_float_register()
            assembly_code += '\tmov.s $f%d, $v1 # using the return value of called function\n' % 10 + (2 * index)
        else:
            index = get_available_register()
            assembly_code += '\tmove $s%d, $v1 # using the return value of called function\n' % index

        return index, assembly_code, func.type, func.deref_depth
    else:
        if len(astnode.children) == 2:
            lhs = astnode.children[0]
            rhs = astnode.children[1]
            lhs_index, lhs_assembly_code, lhs_type, lhs_deref_depth = generate_assembly_code_for_expression(lhs,
                                                                                                            symbol_table,
                                                                                                            global_symbol_table)
            rhs_index, rhs_assembly_code, rhs_type, rhs_deref_depth = generate_assembly_code_for_expression(rhs,
                                                                                                            symbol_table,
                                                                                                            global_symbol_table)
            this_index, this_assembly_code, this_type = generate_assembly_code_for_binary_op(astnode.value, lhs_index,
                                                                                             rhs_index, lhs_type)
            return this_index, lhs_assembly_code + rhs_assembly_code + this_assembly_code, this_type, 0
        elif len(astnode.children) == 1:
            child = astnode.children[0]
            child_index, child_assembly_code, child_type, child_deref_depth = generate_assembly_code_for_expression(
                child, symbol_table,
                global_symbol_table)
            this_index, this_assembly_code, this_type = generate_assembly_code_for_unary_op(astnode.value, child_index,
                                                                                            child_type)
            return this_index, child_assembly_code + this_assembly_code, this_type, 0


def generate_assembly_code_for_assignment(astnode, symbol_table, global_symbol_table):
    if astnode.type == 'ASGN':
        lhs = astnode.children[0]
        rhs = astnode.children[1]
        this_assembly_code = ''
        rhs_index, rhs_assembly_code, rhs_type, rhs_deref_depth = generate_assembly_code_for_expression(rhs,
                                                                                                        symbol_table,
                                                                                                        global_symbol_table)
        if lhs.type == 'DEREF':
            lhs_index, lhs_assembly_code, lhs_type, lhs_deref_depth = generate_register_for_lhs_term(lhs, symbol_table,
                                                                                                     global_symbol_table)
            if rhs_type == 'float' and rhs_deref_depth == 0:
                this_assembly_code += '\t'
                this_assembly_code += 's.s $f%d, 0($s%d)\n' % (10 + 2 * rhs_index, lhs_index)
                free_register(lhs_index)
                free_float_register(rhs_index)
            else:
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
                if rhs_type == 'float' and rhs_deref_depth == 0:
                    this_assembly_code += 's.s $f%d, %d($sp)\n' % (10 + 2 * rhs_index, offset)
                    free_float_register(rhs_index)
                else:
                    this_assembly_code += 'sw $s%d, %d($sp)\n' % (rhs_index, offset)
                    free_register(rhs_index)
                return rhs_assembly_code + this_assembly_code
            elif global_symbol_table.symbol_exists(_id):
                this_assembly_code += '\t'
                if rhs_type == 'float' and rhs_deref_depth == 0:
                    this_assembly_code += 's.s $f%d, global_%s\n' % (10 + 2 * rhs_index, _id)
                    free_float_register(rhs_index)
                else:
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
        cond_index, cond_assembly_code, cond_type, cond_deref_depth = generate_assembly_code_for_expression(
            cfgnode.value, symbol_table,
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
            return_index, return_assembly_code, return_type, return_deref_depth = generate_assembly_code_for_expression(
                return_node_val, symbol_table,
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
    txt += '\n'
    return txt
