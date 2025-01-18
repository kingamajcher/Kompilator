class Array:
    def __init__(self, name, memory_index, first_index, last_index):
        self.name = name
        self.memory_index = memory_index
        if first_index > last_index:
            raise ValueError(f"Error: First index of array {name} is greater than last index.")
        self.first_index = first_index
        self.last_index = last_index

    def __repr__(self):
        return f"{self.memory_index}, [{self.first_index}:{self.last_index}]"
    
    def get_at(self, index):
        if index < self.first_index or index > self.last_index:
            raise IndexError(f"Error: Array index out of bounds.")
        return self.memory_index + (index - self.first_index)
    

class Variable:
    def __init__(self, memory_index):
        self.memory_index = memory_index
        self.initialized = False

    def __repr__(self):
        return f"{self.memory_index}"