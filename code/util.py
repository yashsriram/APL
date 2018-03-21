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


def translate_asgn_or_condn(ast_node):
    """
    Note:
        1. A term is also an expression
        2. If the node is not a term then it is a subtree ending in term leaves
    """
    if len(ast_node.children) == 2:
        lhs = ast_node.children[0]
        rhs = ast_node.children[1]
        if lhs.is_term() and rhs.is_term():
            ret_temp_id = get_next_temp_pk()
            this_cfg = '%s = %s %s %s\n' % (ret_temp_id, lhs.value, ast_node.value, rhs.value)
            return ret_temp_id, this_cfg
        elif not lhs.is_term() and rhs.is_term():
            temp_id, lhs_cfg = translate_asgn_or_condn(lhs)
            ret_temp_id = get_next_temp_pk()
            this_cfg = '%s = %s %s %s\n' % (ret_temp_id, temp_id, ast_node.value, rhs.value)
            return ret_temp_id, lhs_cfg + this_cfg
        elif lhs.is_term() and not rhs.is_term():
            temp_id, rhs_cfg = translate_asgn_or_condn(rhs)
            ret_temp_id = get_next_temp_pk()
            this_cfg = '%s = %s %s %s\n' % (ret_temp_id, lhs.value, ast_node.value, temp_id)
            return ret_temp_id, rhs_cfg + this_cfg
        else:
            temp_id_lhs, lhs_cfg = translate_asgn_or_condn(lhs)
            temp_id_rhs, rhs_cfg = translate_asgn_or_condn(rhs)
            ret_temp_id = get_next_temp_pk()
            this_cfg = '%s = %s %s %s\n' % (ret_temp_id, temp_id_lhs, ast_node.value, temp_id_rhs)
            return ret_temp_id, lhs_cfg + rhs_cfg + this_cfg
    elif len(ast_node.children) == 1:
        child_node = ast_node.children[0]
        if child_node.is_term():
            ret_temp_id = get_next_temp_pk()
            this_cfg = '%s = %s%s\n' % (ret_temp_id, ast_node.value, child_node.value)
            return ret_temp_id, this_cfg
        else:
            temp_id, child_cfg = translate_asgn_or_condn(child_node)
            ret_temp_id = get_next_temp_pk()
            this_cfg = '%s = %s%s\n' % (ret_temp_id, ast_node.value, temp_id)
            return ret_temp_id, child_cfg + this_cfg


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
                    assign_cfg_node = CFGNode('ASGN_BLOCK', block_siblings,
                                              parent=body_cfg_node,
                                              block_number=get_next_block_pk(),
                                              index=len(body_cfg_node.children))
                    body_cfg_node.add_child(assign_cfg_node)
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
            assign_cfg_node = CFGNode('ASGN_BLOCK', block_siblings,
                                      parent=body_cfg_node,
                                      block_number=get_next_block_pk(),
                                      index=len(body_cfg_node.children))
            body_cfg_node.add_child(assign_cfg_node)

        # Give body block the same block number as its first child if it exists
        if len(body_cfg_node.children) > 0:
            body_cfg_node.block_number = body_cfg_node.children[0].block_number

        # Add END_BLOCK cfg node to root body
        if index is None:
            end_cfg_node = CFGNode('END_BLOCK', 'End',
                                   parent=body_cfg_node,
                                   block_number=get_next_block_pk(),
                                   index=len(body_cfg_node.children))
            body_cfg_node.add_child(end_cfg_node)

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
        cc_cfg_node = CFGNode('CONDITION_BLOCK', while_statement.children[0],
                              block_number=block_num,
                              parent=while_cfg_node,
                              index=len(while_cfg_node.children))
        while_cfg_node.add_child(cc_cfg_node)
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
        END_BLOCK

    BODY_BLOCK has block number of its first child if exists else None
    IF_BLOCK & WHILE_BLOCK have block number of its first child which definitely exists
    ASGN_BLOCK & CONDITION_BLOCK have unique block numbers
    END_BLOCK has biggest block number

    ASGN_BLOCK can have only BODY_BLOCK as parent
    BODY_BLOCK can have only IF_BLOCK or WHILE_BLOCK as parent
    IF_BLOCK can have only BODY_BLOCK or IF_BLOCK as parent
    WHILE_BLOCK can have only BODY_BLOCK as parent
    CONDITION_BLOCK can have only IF_BLOCK or WHILE_BLOCK as parent
    END_BLOCK can have only (root) BODY_BLOCK as parent
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

    def goto_block_number(self):
        curr_index = self.index
        parent = self.parent
        # ASGN_BLOCK
        if self.type == 'ASGN_BLOCK':
            # ASGN_BLOCK can have only BODY_BLOCK as parent
            if len(parent.children) == curr_index + 1:
                return parent.goto_block_number()
            else:
                return parent.children[curr_index + 1].block_number
        # BODY_BLOCK
        elif self.type == 'BODY_BLOCK':
            # BODY_BLOCK can have only IF_BLOCK or WHILE_BLOCK as parent
            if parent.type == 'IF_BLOCK':
                return parent.goto_block_number()
            elif parent.type == 'WHILE_BLOCK':
                return parent.children[curr_index - 1].block_number
        # IF_BLOCK
        elif self.type == 'IF_BLOCK':
            # IF_BLOCK can have only BODY_BLOCK or IF_BLOCK as parent
            if parent.type == 'BODY_BLOCK':
                if len(parent.children) == curr_index + 1:
                    return parent.goto_block_number()
                else:
                    return parent.children[curr_index + 1].block_number
            elif parent.type == 'IF_BLOCK':
                return parent.goto_block_number()
        # WHILE_BLOCK
        elif self.type == 'WHILE_BLOCK':
            # WHILE_BLOCK can have only BODY_BLOCK as parent
            if len(parent.children) == curr_index + 1:
                return parent.goto_block_number()
            else:
                return parent.children[curr_index + 1].block_number
        # CONDITION_BLOCK
        elif self.type == 'CONDITION_BLOCK':
            # CONDITION_BLOCK can have only IF_BLOCK or WHILE_BLOCK as parent
            true_goto = None
            false_goto = None
            if parent.type == 'IF_BLOCK':
                # if
                if_cfg_node = parent.children[1]
                if if_cfg_node.block_number is not None:
                    true_goto = if_cfg_node.block_number
                else:
                    true_goto = if_cfg_node.goto_block_number()
                # else
                if len(parent.children) == 2:
                    false_goto = parent.goto_block_number()
                elif len(parent.children) == 3:
                    else_cfg_node = parent.children[2]
                    if else_cfg_node.block_number is not None:
                        false_goto = else_cfg_node.block_number
                    else:
                        false_goto = else_cfg_node.goto_block_number()

            elif parent.type == 'WHILE_BLOCK':
                while_body_cfg_node = parent.children[1]
                if while_body_cfg_node.block_number is not None:
                    true_goto = while_body_cfg_node.block_number
                else:
                    true_goto = while_body_cfg_node.goto_block_number()
                false_goto = parent.goto_block_number()

            return true_goto, false_goto

    def text_repr(self):
        txt = ''
        if self.type == 'ASGN_BLOCK':
            txt += '<bb %d>\n' % self.block_number
            for child in self.value:
                # Assignment
                asgn = child
                lhs = asgn.children[0]
                rhs = asgn.children[1]
                if rhs.is_term():
                    txt += '%s = %s\n' % (lhs.value, rhs.value)
                else:
                    temp_id, rhs_cfg = translate_asgn_or_condn(rhs)
                    this_cfg = '%s = %s\n' % (lhs.value, temp_id)
                    txt += rhs_cfg + this_cfg
            goto = self.goto_block_number()
            txt += 'goto <bb %d>\n' % goto

        elif self.type == 'CONDITION_BLOCK':
            txt += '<bb %d>\n' % self.block_number
            temp_id, child_cfg = translate_asgn_or_condn(self.value)
            txt += child_cfg
            goto_true, goto_false = self.goto_block_number()
            txt += 'if(%s) goto <bb %d>\n' % (temp_id, goto_true)
            txt += 'else goto <bb %d>\n' % goto_false

        elif self.type == 'END_BLOCK':
            txt += '<bb %d>\nEnd' % self.block_number

        return txt

    def tree_text_repr(self):
        if self.type == 'ASGN_BLOCK' or self.type == 'CONDITION_BLOCK' or self.type == 'END_BLOCK':
            return self.text_repr() + '\n'
        else:
            txt = ''
            for child in self.children:
                txt += child.tree_text_repr()
            return txt


class ASTNode:
    def __init__(self, _type, value, is_constant=False, parent=None):
        self.type = _type
        self.value = value
        self.parent = parent
        self.children = []
        self.is_constant = is_constant

    def add_child(self, child):
        self.children.append(child)

    def prepend_child(self, child):
        self.children = [child] + self.children

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

    def tree_text_repr(self, tabs):
        ans = ''
        if self.type == 'VAR' or self.type == 'CONST':
            ans += '\t' * tabs + str(self.type) + '(' + str(self.value) + ')' + '\n'
        elif self.type == 'BODY':
            for i in range(len(self.children)):
                ans += self.children[i].tree_text_repr(tabs)
        else:
            ans += '\t' * tabs + str(self.type) + '\n'
            ans += '\t' * tabs + '(' + '\n'
            for i in range(len(self.children)):
                ans += self.children[i].tree_text_repr(tabs + 1)
                # Don't print last ,
                if i != len(self.children) - 1:
                    ans += '\t' * (tabs + 1) + ',' + '\n'
            ans += '\t' * tabs + ')' + '\n'
        return ans
