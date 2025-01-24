class AST:
    def __init__(self, program):
        self.root = program

    def __str__(self):
        return f"AST:\n{self.root}"

class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, procedures, main):
        self.procedures = procedures
        self.main = main

    def __str__(self):
        return f"Program:\nProcedures:\n{self.procedures}\nMain:\n{self.main}"

class Procedures(ASTNode):
    def __init__(self, procedures=None):
        self.procedures = procedures or []

    def __str__(self):
        return "\n".join([str(proc) for proc in self.procedures])

class Procedure(ASTNode):
    def __init__(self, name, parameters, declarations, commands):
        self.name = name
        self.parameters = parameters
        self.declarations = declarations
        self.commands = commands

    def __str__(self):
        params = ", ".join(str(param) for param in self.parameters)
        decls = "\n".join(str(decl) for decl in self.declarations)
        return f"Procedure {self.name}({params}):\nDeclarations:\n{decls}\nCommands:\n{self.commands}"

class Main(ASTNode):
    def __init__(self, declarations, commands):
        self.declarations = declarations
        self.commands = commands

    def __str__(self):
        decls = "\n".join(str(decl) for decl in self.declarations)
        return f"Main:\nDeclarations:\n{decls}\nCommands:\n{self.commands}"

class Commands(ASTNode):
    def __init__(self, commands):
        self.commands = commands

    def __str__(self):
        return "\n".join(str(command) for command in self.commands)

class Command(ASTNode):
    pass

class Assign(Command):
    def __init__(self, identifier, expression):
        self.identifier = identifier
        self.expression = expression

    def __str__(self):
        return f"Assign {self.identifier} = {self.expression}"

class If(Command):
    def __init__(self, condition, true_commands, false_commands=None):
        self.condition = condition
        self.true_commands = true_commands
        self.false_commands = false_commands

    def __str__(self):
        false_part = f"Else:\n{self.false_commands}" if self.false_commands else ""
        return f"If {self.condition} Then:\n{self.true_commands}\n{false_part}"

class While(Command):
    def __init__(self, condition, commands):
        self.condition = condition
        self.commands = commands

    def __str__(self):
        return f"While {self.condition} Do:\n{self.commands}"

class RepeatUntil(Command):
    def __init__(self, commands, condition):
        self.commands = commands
        self.condition = condition

    def __str__(self):
        return f"Repeat:\n{self.commands}\nUntil {self.condition}"

class For(Command):
    def __init__(self, iterator, start_value, end_value, direction, commands):
        self.iterator = iterator
        self.start_value = start_value
        self.end_value = end_value
        self.direction = direction
        self.commands = commands

    def __str__(self):
        return f"For {self.iterator} From {self.start_value} {self.direction} {self.end_value} Do:\n{self.commands}"

class Read(Command):
    def __init__(self, identifier):
        self.identifier = identifier

    def __str__(self):
        return f"Read {self.identifier}"

class Write(Command):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"Write {self.value}"

class ProcCall(Command):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __str__(self):
        args_str = ", ".join(str(arg) for arg in self.args)
        return f"Call {self.name}({args_str})"

class Declaration(ASTNode):
    def __init__(self, name, array_bounds=None):
        self.name = name
        self.array_bounds = array_bounds

    def __str__(self):
        if self.array_bounds:
            return f"Array {self.name}[{self.array_bounds[0]}:{self.array_bounds[1]}]"
        return f"Variable {self.name}"

class Condition(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __str__(self):
        return f"{self.left} {self.operator} {self.right}"

class Expression(ASTNode):
    pass

class Operation(Expression):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __str__(self):
        return f"({self.left} {self.operator} {self.right})"

class Value(Expression):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Identifier:
    def __init__(self, name, index=None, scope="global"):
        self.name = name
        self.index = index
        self.scope = scope

    def __str__(self):
        if self.index:
            return f"{self.name}[{self.index}] (Scope: {self.scope})"
        return f"{self.name} (Scope: {self.scope})"
