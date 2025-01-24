class Array:
    def __init__(self, memory_index, first_index, last_index):
        self.memory_index = memory_index
        if first_index > last_index:
            raise Exception(f"Error: First index of array is greater than last index.")
        self.first_index = first_index
        self.last_index = last_index

    def __str__(self):
        return f"Array at memory index {self.memory_index}, range [{self.first_index}:{self.last_index}]"

    def get_at(self, index):
        if index < self.first_index or index > self.last_index:
            raise IndexError("Error: Array index out of bounds.")
        return self.memory_index + (index - self.first_index)
    

class Variable:
    def __init__(self, memory_index):
        self.memory_index = memory_index
        self.initialized = False

    def __str__(self):
        status = "Initialized" if self.initialized else "Uninitialized"
        return f"{status} variable at memory index {self.memory_index}"
    

class Iterator:
    def __init__(self, memory_index, limit_index):
        self.memory_index = memory_index
        self.limit_index = limit_index

    def __str__(self):
        return f"Iterator at memory index {self.memory_index}, limit index {self.limit_index}"

    

class Procedure:
    def __init__(self, name, parameters, local_variables, commands, memory_index):
        self.name = name
        self.memory_index = memory_index
        self.parameters = {param: memory_index + i for i, param in enumerate(parameters)}
        self.local_variables = {var: memory_index + len(parameters) + i for i, var in enumerate(local_variables)}
        self.local_arrays = {}
        self.commands = commands
        self.called_procedures = set()
        self.memory_size = len(parameters) + len(local_variables)

        for param in parameters:
            if not param.isidentifier():
                raise Exception(f"Error: Invalid parameter name {param}")

    def is_valid_variable(self, name):
        return name in self.parameters or name in self.local_variables

    def __str__(self):
        return f"Procedure '{self.name}' at memory index {self.memory_index} with parameters {self.parameters}"

    def __str__(self):
        return f"Procedure '{self.name}' at memory index {self.memory_index} with parameters {self.parameters}"


class SymbolTable(dict):
    def __init__(self):
        super().__init__()
        self.memory_index = 0
        self.consts = {}
        self.iterators = {}
        self.procedures = {}

    def add_variable(self, name, scope=None):
        table = scope.local_variables if scope else self
        if name in table or name in self.iterators:
            raise Exception(f"Error: Redeclaration of variable '{name}' in scope.")
        table[name] = Variable(self.memory_index)
        self.memory_index += 1

    def add_array(self, name, first_index, last_index, scope=None):
        table = scope.local_arrays if scope else self
        if name in table or name in self.iterators:
            raise Exception(f"Error: Redeclaration of array '{name}' in scope.")
        if first_index > last_index:
            raise Exception(f"Invalid range for array '{name}'.")
        table[name] = Array(self.memory_index, first_index, last_index)
        self.memory_index += (last_index - first_index + 1)

    def add_const(self, value):
        if value not in self.consts:
            self.consts[value] = self.memory_index
            self.memory_index += 1
        return self.consts[value]
    
    def add_iterator(self, name):
        if name in self or name in self.iterators:
            raise Exception(f"Error: Redeclaration of iterator '{name}'.")
        limit_address = self.memory_index + 1
        self.iterators[name] = Iterator(self.memory_index, limit_address)
        self.memory_index += 2


    def add_procedure(self, name, parameters, local_variables, commands):
        if name in self.procedures:
            raise Exception(f"Error: Redeclaration of procedure '{name}'.")
        if name in self:
            raise Exception(f"Error: Name '{name}' conflicts with variable or array.")
        
        base_memory_index = self.memory_index
        self.memory_index += len(parameters) + len(local_variables)

        procedure = Procedure(name, parameters, local_variables, commands, base_memory_index)
        self.procedures[name] = procedure

        self.validate_procedure(name)

    def validate_procedure(self, name):
        procedure = self.get_procedure(name)
        for called_proc in procedure.called_procedures:
            if called_proc not in self.procedures:
                raise Exception(f"Error: Procedure {called_proc} called in {name} is not defined.")
            if list(self.procedures.keys()).index(called_proc) > list(self.procedures.keys()).index(name):
                raise Exception(f"Error: Procedure {called_proc} must be defined before it is called in {name}.")

    def get_iterator(self, name):
        return self.iterators.get(name)
    
    # getting variable
    def get_variable(self, name, scope=None):
        table = scope.locals if scope else self
        if name in table:
            return table[name]
        elif name in self.iterators:
            return self.iterators[name]
        else:
            raise Exception(f"Error: Undeclared variable '{name}' in scope.")
        
    def get_variable(self, name, scope=None):
        table = scope.local_variables if scope else self
        if name in table:
            return table[name]
        elif name in self.iterators:
            return self.iterators[name]
        else:
            raise Exception(f"Error: Undeclared variable '{name}' in scope.")

    def get_array_at(self, name, index, scope=None):
        table = scope.local_arrays if scope else self
        if name in table:
            try:
                return table[name].get_at(index)
            except AttributeError:
                raise Exception(f"Error: Non-array '{name}' used as an array.")
        else:
            raise Exception(f"Error: Undeclared array '{name}' in scope.")
        
    def get_address(self, target, scope=None):
        table = scope.local_variables if scope else self
        if isinstance(target, str):
            return self.get_variable(target, scope).memory_index
        elif isinstance(target, tuple):
            return self.get_array_at(target[0], target[1], scope)

    def get_procedure(self, name):
        if name in self.procedures:
            return self.procedures[name]
        else:
            raise Exception(f"Error: Undeclared procedure '{name}'.")


if __name__ == "__main__":
    symbol_table = SymbolTable()

    print("=== Adding global variables ===")
    symbol_table.add_variable("x")
    symbol_table.add_variable("y")
    print("Symbol table after adding global variables:")
    print(symbol_table)

    print("\n=== Adding global arrays ===")
    symbol_table.add_array("A", 0, 5)
    symbol_table.add_array("B", 1, 10)
    print("Symbol table after adding global arrays:")
    print(symbol_table)

    print("\n=== Adding iterators ===")
    symbol_table.add_iterator("i")
    symbol_table.add_iterator("j")
    print("Symbol table after adding iterators:")
    print(symbol_table)

    print("\n=== Adding procedures ===")
    symbol_table.add_procedure('proc1', ['a', 'Tb'], ['x'], ['WRITE a;', 'WRITE x;'])
    proc1 = symbol_table.get_procedure("proc1")
    symbol_table.add_variable("z", proc1)
    symbol_table.add_array("C", 0, 3, proc1)
    print(f"Procedure 'proc1': {proc1}")
    print("Local variables of procedure 'proc1':")
    print(proc1.local_variables)
    print("Local arrays of procedure 'proc1':")
    print(proc1.local_arrays)

    print("\n=== Adding second procedure ===")
    symbol_table.add_procedure('proc2', ['p', 'Tq'], ['y', 'z'], ['proc1(p, Tq);', 'WRITE y;', 'WRITE z;'])
    proc2 = symbol_table.get_procedure("proc2")
    symbol_table.add_variable("w", proc2)
    symbol_table.add_array("D", -5, 5, proc2)
    print(f"Procedure 'proc2': {proc2}")
    print("Local variables of procedure 'proc2':")
    print(proc2.local_variables)
    print("Local arrays of procedure 'proc2':")
    print(proc2.local_arrays)

    print("\n=== Accessing variables and arrays ===")
    try:
        addr_x = symbol_table.get_address("x")
        print(f"Address of global variable 'x': {addr_x}")
    except Exception as e:
        print(e)

    try:
        addr_a = symbol_table.get_address(("A", 2))
        print(f"Address of global array 'A' at index 2: {addr_a}")
    except Exception as e:
        print(e)

    try:
        addr_c = symbol_table.get_address(("C", 1), proc1)
        print(f"Address of local array 'C' at index 1 in 'proc1': {addr_c}")
    except Exception as e:
        print(e)

    print("\n=== Error handling ===")
    try:
        symbol_table.add_variable("x")  # Duplicate global variable
    except Exception as e:
        print(f"Expected error: {e}")

    try:
        symbol_table.add_array("A", 0, 5)  # Duplicate global array
    except Exception as e:
        print(f"Expected error: {e}")

    try:
        symbol_table.add_iterator("x")  # Iterator with a name conflicting with a variable
    except Exception as e:
        print(f"Expected error: {e}")

    try:
        addr_out_of_bounds = symbol_table.get_array_at("B", 15)
    except Exception as e:
        print(f"Expected error: {e}")

    print("\n=== Adding third procedure with dependencies ===")
    symbol_table.add_procedure('proc3', ['r'], ['temp'], ['proc2(r, Tb);', 'WRITE temp;'])
    proc3 = symbol_table.get_procedure("proc3")
    print(f"Procedure 'proc3': {proc3}")

    print("\n=== Final symbol table ===")
    print(symbol_table)

