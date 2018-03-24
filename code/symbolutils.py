symbol_tables = {}

current_symbol_table_key = None


def set_current_symbol_table_key(key_val):
    global current_symbol_table_key
    current_symbol_table_key = key_val


class SymbolTable:
    def __init__(self):
        self.rows = {}

    def add_row(self, row):
        if row.id in self.rows.keys():
            raise KeyError
        else:
            self.rows[row.id] = row


class SymbolTableRow:
    def __init__(self, _id, _type, scope, derived_type, width, offset, pointer_to_table):
        self.id = _id
        self.type = _type
        self.scope = scope
        self.derived_type = derived_type
        self.width = width
        self.offset = offset
        self.pointer_to_table = pointer_to_table

    def is_function(self):
        return self.pointer_to_table is not None

    def __repr__(self):
        return '%s %s %s %d %d %d' % (self.id, self.type, self.scope, self.derived_type, self.width, self.offset)
