class Variable:
    def __init__(self, memory_offset, is_local=False, is_parameter=False):
        self.memory_offset = memory_offset
        self.is_local = is_local
        self.is_parameter = is_parameter  
        self.initialized = False

    def __repr__(self):
        return str(self.memory_offset)

class Iterator:
    def __init__(self, memory_offset, limit_memory_offset):
        self.memory_offset = memory_offset
        self.limit_memory_offset = limit_memory_offset

    def __repr__(self):
        return str(self.memory_offset)

class Array:
    def __init__(self, first_index, last_index, memory_offset):
        self.first_index = first_index
        self.last_index = last_index
        self.memory_offset = memory_offset

    def get_memory_index(self, index):
        if index < self.first_index or index > self.last_index:
            raise ValueError(f"Error: Array index '{index}' out of bounds for [{self.first_index} : {self.last_index}].")
        return self.memory_offset + (index - self.first_index)

    def __repr__(self):
        return str(self.memory_offset)
    
class Procedure:
    def __init__(self, name, memory_offset, parameters, local_variables, commands, return_register):
        self.name = name
        self.memory_offset = memory_offset
        self.parameters = parameters
        self.local_variables = local_variables
        self.commands = commands
        self.return_registers = return_register
        self.call_count = 0 

    def __repr__(self):
        return f"{self.name}, {self.memory_offset}, {self.parameters}, {self.local_variables}, {self.commands}, {self.return_register}"

class SymbolTable(dict):
    def __init__(self):
        super().__init__()
        self.memory_offset = 15
        self.iterators = {}
        self.procedures = {}
        self.constants = {}
        self.current_procedure = None 

    def add_variable(self, name):
        if self.current_procedure:
            procedure = self.procedures[self.current_procedure]

            if name in procedure.local_variables:
                raise ValueError(f"Error: Redeclaration of local variable '{name}' in procedure '{self.current_procedure}'.")

            procedure.local_variables[name] = Variable(self.memory_offset, is_local=True)
        
        else:
            if name in self:
                pass
            self[name] = Variable(self.memory_offset)

        self.memory_offset += 1 


    def get_variable(self, name):  
        if name in self:
            return self[name]
        elif name in self.iterators:
            return self.iterators[name]
        else:
            raise ValueError(f"Error: Undeclared variable '{name}'.")
        

    def add_array(self, name, first_index, last_index):
        if name in self:
            raise ValueError(f"Error: Redeclaration of array '{name}'.")
        elif first_index > last_index:
            raise ValueError(f"Error: Invalid range [{first_index} : {last_index}] for array '{name}'.")
        
        array_size = last_index - first_index + 1
        self[name] = Array(first_index, last_index, self.memory_offset)
        self.memory_offset += array_size


    def get_array_at_index(self, name, index):
        if name in self:
            try:
                return self[name].get_memory_index(index)
            except:
                raise ValueError(f"Error: Attempt to use variable '{name}' as an array.")
        else:
            raise ValueError(f"Error: Undeclared array '{name}'.")  
      

    def add_iterator(self, name):
        limit_memory_offset = self.memory_offset
        iterator = Iterator(self.memory_offset + 1, limit_memory_offset) 
        self.iterators[name] = iterator
        self.memory_offset += 2
        return self.memory_offset - 1, limit_memory_offset
    

    def get_iterator(self, name):
        if name in self.iterators:
            iterator = self.iterators[name]
            return iterator
        else:
            raise ValueError(f"Error: Undeclared iterator '{name}'.")
        

    def add_procedure(self, name, parameters, local_variables, commands):
        if name in self.procedures:
            raise ValueError(f"Error: Redeclaration of procedure '{name}'.")
        if name in self:
            raise ValueError(f"Error: Name '{name}' is already in use.")

        self.current_procedure = name

        parameters_memory = {}
        for parameter in parameters:
            if isinstance(parameter, tuple):
                if parameter[0].startswith("T"):
                    array_name = parameter[1]
                    parameters_memory[array_name] = Array(None, None, self.memory_offset) 
                    self.memory_offset += 1
                else:
                    raise ValueError(f"Error: invalid parameter '{parameter}' in procedure '{name}'")
            else:
                parameters_memory[parameter] = Variable(self.memory_offset, is_parameter=True)
                self.memory_offset += 1  

        local_variables_memory = {}
        for variable in local_variables:
            local_variables_memory[variable] = Variable(self.memory_offset, is_local=True)
            self.memory_offset += 1
        
        return_memory = [Variable(self.memory_offset + i, is_local=True) for i in range(100)] 
        self.memory_offset += 100

        if name not in self.procedures:
            self.procedures[name] = Procedure(name, None, parameters_memory, local_variables_memory, commands, return_memory)  
        
        self.is_procedure_valid(name)
        self.current_procedure = None  

    
    def is_procedure_valid(self, name):
        procedure  = self.get_procedure(name)
        commands = procedure.commands

        for command in commands:
            if command[0] == "proc_call":
                called_procedure = command[1]
                if called_procedure not in self.procedures:
                    raise ValueError(f"Error: Procedure '{called_procedure}' does not exist.")
                if list(self.procedures.keys()).index(called_procedure) > list(self.procedures.keys()).index(name):
                    raise ValueError(f"Error: Cannot call procedure '{called_procedure}' before it is defined.")

            
    def get_procedure(self, name):
        if name in self.procedures:
            procedure = self.procedures[name]
            return procedure
        else:
            raise ValueError(f"Error: Undeclared procedure '{name}'.")
        

    def get_address_in_procedure(self, name):
        if self.current_procedure:
            procedure = self.procedures[self.current_procedure]
            if name in procedure.parameters:
                return procedure.parameters[name]  
            elif name in procedure.local_variables:
                return procedure.local_variables[name]
            

    def get_address(self, name):
        if type(name) == str:
            return self.get_variable(name).memory_offset
        else:
            array_name = name[0]
            index = name[1]
            return self.get_array_at_index(array_name, index) 