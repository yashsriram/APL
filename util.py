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


def generate_CFG(ast_node, index=None):
    if ast_node.type == 'BODY':
        body_cfg_node = CFGNode('BODY_BLOCK', 'body_block', ast_node.is_constant, index=index)
        block_siblings = []
        for child in ast_node.children:
            if child.type == 'ASGN':
                block_siblings.append(child)
            else:
                # Merge all contiguous assignment statements into one MASTNode
                if len(block_siblings) != 0:
                    assign_block = CFGNode('ASGN_BLOCK', block_siblings, 
                        parent=body_cfg_node, 
                        block_number=get_next_block_pk(), 
                        index=len(body_cfg_node.children))
                    body_cfg_node.add_child(assign_block)
                    print(generate_block_text(assign_block))
                    block_siblings = []
                if child.type == 'IF':
                    # If node
                    if_cfg_node = generate_CFG(child, len(body_cfg_node.children))
                    if_cfg_node.parent = body_cfg_node
                    body_cfg_node.add_child(if_cfg_node)
                elif child.type == 'WHILE':
                    # While node
                    while_cfg_node = generate_CFG(child, len(body_cfg_node.children))
                    # Attach While node to body_cfg_node
                    while_cfg_node.parent = body_cfg_node
                    body_cfg_node.add_child(while_cfg_node)

        # Merge all contiguous assignment statements into one MASTNode
        if len(block_siblings) != 0:
            assign_block = CFGNode('ASGN_BLOCK', block_siblings, 
                parent=body_cfg_node, 
                block_number=get_next_block_pk(),
                index=len(body_cfg_node.children))
            body_cfg_node.add_child(assign_block)
            print(generate_block_text(assign_block))

        # Give body block the same block number as its first child if it exists
        if len(body_cfg_node.children) > 0:
            body_cfg_node.block_number = body_cfg_node.children[0].block_number

        return body_cfg_node
    elif ast_node.type == 'IF':
        if_statement = ast_node
        # Give if block the same block number as condition block (its first child)
        block_num = get_next_block_pk()
        if_cfg_node = CFGNode('IF_BLOCK', 'if_block', if_statement.is_constant, 
            block_number=block_num, 
            index=index)
        # Compound condition node
        cc_cfg_node = CFGNode('CONDITION_BLOCK', if_statement.children[0], 
            block_number=block_num, 
            parent=if_cfg_node,
            index=len(if_cfg_node.children))
        if_cfg_node.add_child(cc_cfg_node)
        print(generate_block_text(cc_cfg_node))
        # If body node
        if_body = if_statement.children[1]
        if_body_cfg_node = generate_CFG(if_body, len(if_cfg_node.children))
        if_body_cfg_node.parent = if_cfg_node
        if_cfg_node.add_child(if_body_cfg_node)
        # Else body node
        if len(if_statement.children) == 3:
            else_body = if_statement.children[2]
            else_body_cfg_node = generate_CFG(else_body, len(if_cfg_node.children))
            else_body_cfg_node.parent = if_cfg_node
            if_cfg_node.add_child(else_body_cfg_node)
        return if_cfg_node
    elif ast_node.type == 'WHILE':
        while_statement = ast_node
        # Give while block the same block number as condition block (its first child)
        block_num = get_next_block_pk()
        while_cfg_node = CFGNode('WHILE_BLOCK', 'while_block', while_statement.is_constant, 
            block_number=block_num, 
            index=index)
        # Compound condition node
        cc_cfg_node = CFGNode('CONDITION_BLOCK',while_statement.children[0], 
            block_number=block_num, 
            parent=while_cfg_node,
            index=len(while_cfg_node.children))
        while_cfg_node.add_child(cc_cfg_node)
        print(generate_block_text(cc_cfg_node))
        # While body node
        while_body = while_statement.children[1]
        while_body_cfg_node = generate_CFG(while_body, len(while_cfg_node.children))
        while_body_cfg_node.parent = while_cfg_node
        while_cfg_node.add_child(while_body_cfg_node)
        return while_cfg_node


class CFGNode:
    """
    type can be:
        BODY_BLOCK
        WHILE_BLOCK
        IF_BLOCK
        ASGN_BLOCK -> value = list of pointers to asgn ast nodes
        CONDITION_BLOCK -> value = pointer to compound condition ast node

    BODY_BLOCK has block number of its first child if exists else None
    IF_BLOCK & WHILE_BLOCK have block number of its first child which definitely exists
    ASGN_BLOCK & CONDITION_BLOCK have unique block numbers
    """
    def __init__(self, _type, value, is_constant=False, parent=None, block_number=None, index=None):
        self.type = _type
        self.value = value
        self.parent = parent
        self.is_constant = is_constant
        self.children = []
        self.block_number = block_number
        self.index = index

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

