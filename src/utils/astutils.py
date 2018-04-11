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

    def is_function_call(self):
        """
        Returns whether the token stream comming from this node is a function call or not.
        """
        if self.type == 'FUNCTION_CALL':
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
            ans += '\t' * tabs + 'CALL ' + id_node.value + '(' + '\n'
            for i in range(len(arg_strings)):
                ans += arg_strings[i]
                # Don't print last ,
                if i != len(arg_strings) - 1:
                    ans += '\t' * (tabs + 1) + ',' + '\n'
            ans += '\t' * tabs + ')\n'
        elif self.type == 'RETURN':
            return_term = self.children
            ans += '\t' * tabs + 'RETURN' + '\n'
            ans += '\t' * tabs + '(' + '\n'
            if len(return_term) == 1:
                ans += '\t' * tabs + return_term[0].tree_text_repr(tabs + 1)
            ans += '\t' * tabs + ')' + '\n'

        elif self.type == 'FUNCTION':
            type_node, id_node, params_list_node, body_node, return_node = self.children
            # FUNCTION
            ans += '\t' * tabs + 'FUNCTION ' + self.value + '\n'
            param_list = ''
            _type = None
            # Add params from param_list_node to param_dict
            for i, child in enumerate(params_list_node.children):
                if i % 2 == 0:
                    # Even child represents type
                    _type = child.value
                else:
                    _id = child.value
                    param_list += _type + ' ' + _id
                    if i != len(params_list_node.children) - 1:
                        param_list += ', '
            param_dict = '(' + param_list + ')'
            ans += '\t' * tabs + 'PARAMS ' + param_dict + '\n'
            ans += '\t' * tabs + 'RETURNS ' + type_node.value + '\n'
            # BODY
            ans += '\t' * tabs + body_node.tree_text_repr(tabs + 1)
            # RETURN
            if self.value != 'main':
                ans += '\t' * tabs + return_node.tree_text_repr(tabs)
            ans += '\n'
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
