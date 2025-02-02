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
        self.call_count = 0

    def __str__(self):
        return (f"Procedure {self.name}:\n"
                f"  Parameters: {self.parameters}\n"
                f"  Local Variables: {self.local_variables}\n"
                f"  Commands: {self.commands}\n"
                f"  Memory Offset: {self.memory_offset}\n"
                f"  Return Register: {self.return_register}\n")
    

class SymbolTable(dict):
    def __init__(self):
        super().__init__()
        self.memory_offset = 20
        #self.consts = {}
        self.iterators = {}
        self.procedures = {}
        self.current_procedure = None

    # adding variables
    def add_variable(self, name):
        if self.current_procedure != None:
            procedure = self.procedures[self.current_procedure]
            if name in procedure.local_variables:
                raise Exception(f"Error: Redeclaration of variable '{name}' in procedure {procedure}.")
            procedure.local_variables[name] = Variable(self.memory_offset, is_local=True)
        else:     
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
    """def add_const(self, value):
        if value not in self.consts:
            self.consts[value] = self.memory_offset
            self.memory_offset += 1
        return self.consts[value]"""
    
    # adding iterators
    def add_iterator(self, name):
        limit_address = self.memory_offset
        self.iterators[name] = Iterator(self.memory_offset + 1, limit_address)
        self.memory_offset += 2
        return self.memory_offset - 1, limit_address

    # adding procedure
    def add_procedure(self, name, parameters, local_variables, commands):
        if name in self.procedures or name in self:
            raise Exception(f"Error: Redeclaration of procedure {name}")
        else:
            self.current_procedure = name

            parameters_memory = {}
            for parameter in parameters:
                if isinstance(parameter, tuple) and parameter[0] == "T":
                    array_name = parameter[1]
                    parameters_memory[array_name] = Array(self.memory_offset, None, None)
                    self.memory_offset += 1
                else:
                    parameters_memory[parameter] = Variable(self.memory_offset, is_parameter=True)
                    self.memory_offset += 1

            local_variables_memory = {}
            for local_variable in local_variables:
                local_variables_memory[local_variable] = Variable(self.memory_offset, is_local=True)
                self.memory_offset += 1
            
            return_memory = []
            for i in range(10):
                return_memory.append(Variable(self.memory_offset + i, is_local=True))
            self.memory_counter += 10

            self.procedures[name] = Procedure(name, parameters_memory, local_variables_memory, commands, None, return_memory)

            self.is_procedure_valid(name)
            self.current_procedure = None

    # checking if procedure is valid
    def is_procedure_valid(self, name):
        procedure  = self.get_procedure(name)
        commands = procedure.commands

        for command in commands:
            if command[0] == "proc_call":
                called_procedure = command[1]
                if called_procedure not in self.procedures:
                    raise Exception(f"Error: Procedure '{called_procedure}' is not declared.")
                procedure_keys = list(self.procedures)
                if procedure_keys.index(called_procedure) > procedure_keys.index(name):
                    raise Exception(f"Error: Procedure {called_procedure} is called before it is defined.")


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
        
    # getting address in procedure
    def get_address_in_procedure(self, name):
        if self.current_procedure != None:
            procedure = self.procedures[self.current_procedure]
            if name in procedure.parameters:
                return procedure.parameters[name]
            elif name in procedure.local_variables:
                return procedure.local_variables[name]
            else:
                raise Exception(f"Error: Undeclared variable '{name}' in procedure {procedure}.")
    
    
    # getting procedure
    def get_procedure(self, name):
        if name in self.procedures:
            return self.procedures[name]
        else:
            raise Exception(f"Error: Undeclared procedure'{name}'.")