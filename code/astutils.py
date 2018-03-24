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
