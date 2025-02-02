class Array:
    def __init__(self, memory_offset, first_index, last_index):
        self.memory_offset = memory_offset
        if first_index > last_index:
            raise Exception (f"Error: First index of array is greater than last index.")
        self.first_index = first_index
        self.last_index = last_index

    def __str__(self):
        return f"Array '{self.name}' at memory index {self.memory_offset}, range [{self.first_index}:{self.last_index}]"
    
    def get_memory_index(self, index):
        if index < self.first_index or index > self.last_index:
            raise IndexError(f"Error: Array index out of bounds.")
        return self.memory_offset + (index - self.first_index) + 1
    

class Variable:
    def __init__(self, memory_offset, is_local = False, is_parameter = False):
        self.memory_offset = memory_offset
        self.is_local = is_local
        self.is_parameter = is_parameter
        self.initialized = False

    def __str__(self):
        status = "Initialized" if self.initialized else "Uninitialized"
        return f"{status} variable at memory index {self.memory_offset}"
    

class Iterator:
    def __init__(self, memory_offset, limit_index):
        self.memory_offset = memory_offset
        self.limit_index = limit_index

    def __str__(self):
        return f"Iterator at memory index {self.memory_offset}, limit index {self.limit_index}"

    

class Procedure:
    def __init__(self, name, parameters, local_variables, commands, memory_offset, return_register):
        self.name = name
        self.parameters = parameters
        self.local_variables = local_variables
        self.commands = commands
        self.memory_offset = memory_offset
        self.return_register = return_register

    def __str__(self):
        params_str = ', '.join(f"{p}({offset})" for p, offset in self.parameters.items())
        locals_str = ', '.join(f"{v}({offset})" for v, offset in self.local_variables.items())
        commands_str = '\n    '.join(self.commands)
        return (f"Procedure {self.name}:\n"
                f"  Parameters: {params_str}\n"
                f"  Local Variables: {locals_str}\n"
                f"  Commands:\n    {commands_str}")
    

class SymbolTable(dict):
    def __init__(self):
        super().__init__()
        self.memory_offset = 20
        self.consts = {}
        self.iterators = {}
        self.procedures = {}

    # adding variables
    def add_variable(self, name):
        if name in self:
            raise Exception(f"Error: Redeclaration of variable '{name}'.")
        self[name] = Variable(self.memory_offset)
        self.memory_offset += 1

    # adding arrays
    def add_array(self, name, first_index, last_index):
        if name in self:
            raise Exception(f"Error: Redeclaration of array '{name}'.")
        elif first_index > last_index:
            raise Exception(f"Invalid range for array '{name}'.")
        self[name] = Array(self.memory_offset, first_index, last_index)
        self.memory_offset += (last_index - first_index + 1)

    # adding constants
    def add_const(self, value):
        if value not in self.consts:
            self.consts[value] = self.memory_offset
            self.memory_offset += 1
        return self.consts[value]
    
    # adding iterators
    def add_iterator(self, name):
        limit_address = self.memory_offset
        self.iterators[name] = Iterator(self.memory_offset + 1, limit_address)
        self.memory_offset += 2
        return self.memory_offset - 1, limit_address

    # adding procedure
    def add_procedure(self, name, parameters, local_variables, commands):
        if name in self.procedures:
            raise Exception(f"Error: Redeclaration of procedure {name}")

        base_memory_offset = self.memory_offset
        memory_size = len(parameters) + len(local_variables)
        self.memory_offset += memory_size

        procedure = Procedure(name, parameters, local_variables, commands, base_memory_offset)
        self.procedures[name] = procedure

        self.is_procedure_valid(name)


    def is_procedure_valid(self, name):
        procedure = self.get_procedure(name)

        for called_proc in procedure.called_procedures:
            if called_proc not in self.procedures:
                raise Exception(f"Error: Procedure {called_proc} called in {name} is not defined")
            if list(self.procedures.keys()).index(called_proc) > list(self.procedures.keys()).index(name):
                raise Exception(f"Error: Procedure {called_proc} must be defined before it is called in {name}")
            
    def is_index_valid(self, array_name, index):
        # Sprawdzenie, czy podana tablica istnieje
        if array_name not in self or not isinstance(self[array_name], Array):
            raise Exception(f"Error: '{array_name}' is not a declared array.")

        array = self[array_name]

        # Jeśli indeks jest liczbą całkowitą, sprawdź, czy mieści się w zakresie
        if isinstance(index, int):
            return array.first_index <= index <= array.last_index

        # Jeśli indeks jest zmienną, pobierz jej wartość
        if isinstance(index, str):
            # Użycie istniejącej metody `get_variable` do walidacji zmiennej
            variable = self.get_variable(index)
            if not isinstance(variable, Variable):
                raise Exception(f"Error: '{index}' is not a valid variable.")

            # Zakładamy, że w runtime zmienna będzie miała przypisaną wartość.
            # Tymczasowo symulujemy jej wartość jako `0` dla demonstracji.
            resolved_value = variable.memory_offset  # Symulacja - zastąp właściwą wartością runtime

            # Sprawdź, czy zdekodowana wartość mieści się w zakresie tablicy
            return array.first_index <= resolved_value <= array.last_index

        # Jeśli typ indeksu jest nieobsługiwany, zgłoś błąd
        raise TypeError(f"Error: Unsupported index type '{type(index).__name__}'.")

    # getting iterator
    def get_iterator(self, name):
        if name in self.iterators:
            iterator = self.iterators[name]
            return iterator.memory_offset, iterator.limit_index
        else:
            raise Exception(f"Undeclared iterator '{name}'.")
    
    # getting variable
    def get_variable(self, name):
        if name in self:
            return self[name]
        elif name in self.iterators:
            return self.iterators[name]
        else:
            raise Exception(f"Error: Undeclared variable '{name}'.")
        
    # getting array at value
    def get_array_at(self, name, index):
        if name in self:
            try:
                return self[name].get_memory_index(index)
            except AttributeError:
                raise Exception(f"Error: Non-array '{name}' used as an array.")
        else:
            raise Exception(f"Error: Undeclared array '{name}'.")
        
    # getting address of variable or array
    def get_address(self, name):
        if type(name) == str:
            return self.get_variable(name).memory_offset
        else:
            return self.get_array_at(name[0], name[1])
    

        
    # getting procedure
    def get_procedure(self, name):
        if name in self.procedures:
            return self.procedures[name]
        else:
            raise Exception(f"Error: Undeclared procedure'{name}'.")
        


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
    symbol_table.add_procedure('proc1', ['a', 'Tb'], ['x'], ['WRITE a;', 'WRITE x;'])
    print(f"Procedura 'proc1': {symbol_table.get_procedure('proc1')}")

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