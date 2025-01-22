class Array:
    def __init__(self, name, memory_index, first_index, last_index):
        self.name = name
        self.memory_index = memory_index
        if first_index > last_index:
            raise ValueError(f"Error: First index of array {name} is greater than last index.")
        self.first_index = first_index
        self.last_index = last_index

    def __str__(self):
        return f"Array '{self.name}' at memory index {self.memory_index}, range [{self.first_index}:{self.last_index}]"
    
    def get_at(self, index):
        if index < self.first_index or index > self.last_index:
            raise IndexError(f"Error: Array index out of bounds.")
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
    def __init__(self, name, memory_index, parameters):
        self.name = name
        self.memory_index = memory_index
        self.parameters = parameters
        self.locals = SymbolTable()

    def __str__(self):
        return f"Procedure '{self.name}' at memory index {self.memory_index} with parameters {self.parameters}"
    

class SymbolTable(dict):
    def __init__(self):
        super().__init__()
        self.memory_index = 0
        self.consts = {}
        self.iterators = {}
        self.procedures = {}

    # adding variables
    def add_variable(self, name):
        if name in self or name in self.iterators:
            raise ValueError(f"Error: Redeclaration of variable '{name}'.")
        self[name] = Variable(self.memory_index)
        self.memory_index += 1

    # adding arrays
    def add_array(self, name, first_index, last_index):
        if name in self or name in self.iterators:
            raise ValueError(f"Error: Redeclaration of array '{name}'.")
        if first_index > last_index:
            raise ValueError(f"Invalid range for array '{name}'.")
        self[name] = Array(name, self.memory_index, first_index, last_index)
        self.memory_index += (last_index - first_index + 1)

    # adding constants
    def add_const(self, value):
        if value not in self.consts:
            self.consts[value] = self.memory_index
            self.memory_index += 1
        return self.consts[value]
    
    # adding iterators
    def add_iterator(self, name):
        if name in self or name in self.iterators:
            raise ValueError(f"Error: Redeclaration of iterator '{name}'.")
        limit_address = self.memory_index + 1
        self.iterators[name] = Iterator(self.memory_index, limit_address)
        self.memory_index += 2

    # adding procedure
    def add_procedure(self, name, start_address, parameters):
        if name in self.procedures:
            raise ValueError(f"Error: Redeclaration of procedure '{name}'.")
        self.procedures[name] = Procedure(name, start_address, parameters)

    # getting iterator
    def get_iterator(self, name):
        return name in self.iterators
    
    # getting variable
    def get_variable(self, name):
        if name in self:
            return self[name]
        elif name in self.iterators:
            return self.iterators[name]
        else:
            raise ValueError(f"Error: Undeclared variable '{name}'.")
        
    # getting array at value
    def get_array_at(self, name, index):
        if name in self:
            try:
                return self[name].get_at(index)
            except AttributeError:
                raise ValueError(f"Error: Non-array '{name}' used as an array.")
        else:
            raise ValueError(f"Error: Undeclared array '{name}'.")
        
    # getting address of variable or array
    def get_address(self, target):
        if isinstance(target, str):
            return self.get_variable(target).memory_index
        elif isinstance(target, tuple):
            return self.get_array_at(target[0], target[1])
        
    # getting procedure
    def get_procedure(self, name):
        if name in self.procedures:
            return self.procedures[name]
        else:
            raise ValueError(f"Error: Undeclared procedure'{name}'.")
        


if __name__ == "__main__":
    symbol_table = SymbolTable()

    print("=== Dodawanie zmiennych ===")
    symbol_table.add_variable("x")
    symbol_table.add_variable("y")
    print("Tablica symboli po dodaniu zmiennych:")
    print(symbol_table)

    print("\n=== Dodawanie tablic ===")
    symbol_table.add_array("arr", -10, 10)
    symbol_table.add_array("matrix", 0, 4)
    print("Tablica symboli po dodaniu tablic:")
    print(symbol_table)

    print("\n=== Pobieranie elementów tablicy ===")
    print(f"Adres arr[-5]: {symbol_table.get_array_at('arr', -5)}")
    print(f"Adres matrix[2]: {symbol_table.get_array_at('matrix', 2)}")

    print("\n=== Dodawanie stałych ===")
    addr1 = symbol_table.add_const(42)
    addr2 = symbol_table.add_const(100)
    addr3 = symbol_table.add_const(42)
    print(f"Adres stałej 42: {addr1}")
    print(f"Adres stałej 100: {addr2}")
    print(f"Adres stałej 42 (ponownie): {addr3}")

    print("\n=== Dodawanie iteratorów ===")
    symbol_table.add_iterator("i")
    symbol_table.add_iterator("j")
    print("Tablica symboli po dodaniu iteratorów:")
    print("Iteratory:", symbol_table.iterators)

    print("\n=== Dodawanie procedury ===")
    symbol_table.add_procedure(
        "foo",
        start_address=100,
        parameters=[("a", "int"), ("Tarr", "array")]
    )
    print(f"Procedura 'foo': {symbol_table.get_procedure('foo')}")

    print("\n=== Pobieranie adresu zmiennej i tablicy ===")
    print(f"Adres zmiennej 'x': {symbol_table.get_address('x')}")
    print(f"Adres tablicy 'arr[-5]': {symbol_table.get_address(('arr', -5))}")

    print("\n=== Obsługa błędów ===")
    try:
        symbol_table.add_variable("x")
    except Exception as e:
        print(f"{e}")

    try:
        symbol_table.get_array_at("matrix", 10)
    except Exception as e:
        print(f"{e}")

    try:
        symbol_table.get_variable("unknown")
    except Exception as e:
        print(f"{e}")