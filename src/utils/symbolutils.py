global_symbol_table = None

symbol_table_stack = []


def get_non_func_symbol_from_stack(_id):
    for i in range(len(symbol_table_stack)):
        ri = len(symbol_table_stack) - i - 1
        sym = symbol_table_stack[ri].get_non_func_symbol(_id)
        if sym is not False:
            return sym
    sym = global_symbol_table.get_non_func_symbol(_id)
    if sym is not False:
        return sym
    raise KeyError("Symbol not found")


class SymbolTable:
    def __init__(self):
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

    def get_ordered_param_symbols(self):
        param_symbols = []
        for sym in self.symbols.values():
            if sym.param_index is not None:
                param_symbols.append(sym)
        param_symbols.sort(key=lambda symbol: symbol.param_index)
        return param_symbols


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

    def __eq__(self, other):
        return (self.type, self.scope, self.deref_depth, self.width, self.param_index) \
               == (other.type, other.scope, other.deref_depth, other.width, other.param_index)

    def __repr__(self):
        return '%s %s %s %d %d %d' % (self.id, self.type, self.scope, self.deref_depth, self.width, self.offset)
