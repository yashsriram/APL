def get_non_func_symbol_from_stack(_id, global_symbol_table, symbol_table_stack):
    for i in range(len(symbol_table_stack)):
        ri = len(symbol_table_stack) - i - 1
        sym = symbol_table_stack[ri].get_non_func_symbol(_id)
        if sym is not False:
            return sym
    sym = global_symbol_table.get_non_func_symbol(_id)
    if sym is not False:
        return sym
    raise KeyError


def procedure_table_text_repr(symbol_table):
    ans = 'Procedure table :-\n-----------------------------------------------------------------\n'
    ans += 'Name\t|\tReturn Type\t|\tParameter List\n'
    procedure_list = []
    for func_id, symbol in symbol_table.symbols.items():
        if symbol.is_function():
            return_type_txt = symbol.type + '*' * symbol.deref_depth
            params_txt_list = []
            ordered_params = symbol.its_table.get_params_in_order()
            for ordered_param in ordered_params:
                _id, _type, deref_depth = ordered_param
                params_txt_list.append('%s %s' % (_type, '*' * deref_depth + _id))
            params_txt = ', '.join(params_txt_list)
            proc_txt = '%s\t|\t%s\t\t|\t%s\n' % (func_id, return_type_txt, params_txt)
            procedure_list.append((func_id,proc_txt))
    procedure_list.sort(key=lambda procedure: procedure[0])
    for procedure in procedure_list:
        if procedure[0] != 'main':
            ans += procedure[1]
    ans += '-----------------------------------------------------------------\n'
    return ans

def variable_table_text_repr(symbol_table, name):
    ans = 'Variable table :-\n'
    ans += '-----------------------------------------------------------------\n'
    ans += 'Name\t|\tScope\t\t|\tBase Type\t|\tDerived Type\n'
    ans += '-----------------------------------------------------------------\n'
    ans += symbol_table.variable_table_text_repr(name)
    ans += '-----------------------------------------------------------------\n'
    ans += '-----------------------------------------------------------------\n'
    return ans



class SymbolTable:
    def __init__(self, _type=None, deref_depth=None):
        self.type = _type
        self.deref_depth = deref_depth
        self.symbols = {}

    def symbol_exists(self, _id):
        return _id in self.symbols.keys()

    def add_symbol(self, symbol):
        self.symbols[symbol.id] = symbol

    def get_symbol(self, _id):
        return self.symbols[_id]

    def get_non_func_symbol(self, _id):
        try:
            symbol = self.symbols[_id]
            if not symbol.is_function():
                return symbol
            else:
                return False
        except KeyError:
            return False

    def get_param_signature(self):
        """
        returns only type, deref depth and index of param
        does not care about its name
        """
        param_symbols = []
        for sym in self.symbols.values():
            if sym.param_index is not None:
                param_symbols.append(sym)
        param_symbols.sort(key=lambda symbol: symbol.param_index)
        param_req_symbols = []
        for sym in param_symbols:
            param_req_symbols.append((sym.type, sym.deref_depth, sym.param_index))
        return param_req_symbols

    def get_params_in_order(self):
        """
        returns params of the symbol table if it is a function in their defined order
        """
        param_symbols = []
        for sym in self.symbols.values():
            if sym.param_index is not None:
                param_symbols.append(sym)
        param_symbols.sort(key=lambda symbol: symbol.param_index)
        param_req_symbols = []
        for sym in param_symbols:
            param_req_symbols.append((sym.id, sym.type, sym.deref_depth))
        return param_req_symbols

    def variable_table_text_repr(self, name):
        ans = ''
        param_list = []
        func_list = []
        for _id, symbol in self.symbols.items():
            if symbol.is_function():
                txt = symbol.its_table.variable_table_text_repr(symbol.id)
                func_list.append((symbol.id,txt))
            else:
                txt = '%s\t\t|\t%s\t|\t%s\t|\t%s\n' % (symbol.id, 'procedure ' + name, symbol.type, '*' * symbol.deref_depth)
                param_list.append((symbol.id,txt))
        param_list.sort(key=lambda tup: tup[0])
        func_list.sort(key=lambda tup: tup[0])
        for param in param_list:
            ans += param[1]
        for func in func_list:
            ans += func[1]
        return ans


class Symbol:
    """
    param_index = None for non param symbols (global, local etc...)
        for others it means the symbol is (index)th param of function
    """
    GLOBAL_SCOPE = 'global_scope'
    LOCAL_SCOPE = 'local_scope'
    PARAM_SCOPE = 'param_scope'

    def __init__(self, _id, _type, scope, deref_depth, width, offset=0, its_table=None, param_index=None,
                 is_prototype=False):
        self.id = _id
        self.type = _type
        self.scope = scope
        self.deref_depth = deref_depth
        self.width = width
        self.offset = offset
        # Used when symbol is a function
        self.its_table = its_table
        self.is_prototype = is_prototype
        # Used when symbol is a param
        self.param_index = param_index

    def is_function(self):
        return self.its_table is not None

    def __repr__(self):
        return '%s %s %s %d %d %d' % (self.id, self.type, self.scope, self.deref_depth, self.width, self.offset)
