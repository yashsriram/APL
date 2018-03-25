class ASTNode:
    def __init__(self, _type, value, is_constant=False, parent=None):
        self.type = _type
        self.value = value
        self.children = []
        self.parent = parent
        self.is_constant = is_constant

    def append_child(self, child):
        self.children.append(child)
        child.parent = self

    def prepend_child(self, child):
        self.children = [child] + self.children
        child.parent = self

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

    def tree_text_repr(self, tabs=0):
        ans = ''
        if self.type == 'VAR' or self.type == 'CONST':
            ans += '\t' * tabs + str(self.type) + '(' + str(self.value) + ')' + '\n'
        elif self.type == 'BODY':
            for i in range(len(self.children)):
                ans += self.children[i].tree_text_repr(tabs)
        elif self.type == 'FUNCTION_CALL':
            id_node, arg_list_node = self.children
            arg_strings = []
            for arg in arg_list_node.children:
                arg_strings.append(arg.tree_text_repr(tabs + 1))
            ans += '\t' * tabs + 'call ' + id_node.value + '\n'
            ans += '\t' * tabs + '(\n'
            ans += ''.join(arg_strings)
            ans += '\t' * tabs + ')\n'
        elif self.type == 'RETURN':
            pass
        elif self.type == 'FUNCTION':
            type_node, id_node, params_list_node, body_node = self.children
            # FUNCTION
            ans += '\t' * tabs + 'FUNCTION ' + self.value + '\n'
            if len(params_list_node.children) > 0:
                param_dict = {}
                _type = None
                # Add params from param_list_node to param_dict
                for i, child in enumerate(params_list_node.children):
                    if i % 2 == 0:
                        # Even child represents type
                        _type = child.value
                    else:
                        _id = child.value
                        param_dict[_id] = _type
                ans += '\t' * tabs + 'PARAMS ' + str(param_dict) + '\n'
            # RETURNS
            if type_node.value != 'void':
                ans += '\t' * tabs + 'RETURNS ' + type_node.value + '\n'
            # BODY
            ans += '\t' * tabs + body_node.tree_text_repr(tabs + 1)
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
