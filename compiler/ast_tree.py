class AST:
    def __init__(self, program):
        self.root = program

class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, procedures, main):
        self.procedures = procedures
        self.main = main

class Procedures(ASTNode):
    def __init__(self, procedures = None):
        self.procedures = procedures

class Procedure(ASTNode):
    def __init__(self, name, parameters, declarations, commands):
        self.name = name
        self.parameters = parameters
        self.declarations = declarations
        self.commands = commands

class Main(ASTNode):
    def __init__(self, declarations, commands):
        self.declarations = declarations
        self.commands = commands

class Commands(ASTNode):
    def __init__(self, commands):
        self.commands = commands

class Command(ASTNode):
    pass

class Assign(Command):
    def __init__(self, identifier, expression):
        self.identifier = identifier
        self.expression = expression

class If(Command):
    def __init__(self, condition, true_commands, false_commands = None):
        self.condition = condition
        self.true_commands = true_commands
        self.false_commands = false_commands

class While(Command):
    def __init__(self, condition, commands):
        self.condition = condition
        self.commands = commands

class RepeatUntil(Command):
    def __init__(self, commands, condition):
        self.commands = commands
        self.condition = condition

class For(Command):
    def __init__(self, iterator, start_value, end_value, direction, commands):
        self.iterator = iterator
        self.start_value = start_value
        self.end_value = end_value
        self.direction = direction
        self.commands = commands

class Read(Command):
    def __init__(self, identifier):
        self.identifier = identifier

class Write(Command):
    def __init__(self, value):
        self.value = value

class ProcCall(Command):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class Declaration(ASTNode):
    def __init__(self, name, array_bounds = None):
        self.name = name
        # if variable then array_bounds = None
        self.array_bounds = array_bounds

class Condition(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
    
class Expression(ASTNode):
    pass

class Operation(Expression):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class Value(Expression):
    def __init__(self, value):
        self.value = value

class Identifier(Value):
    def __init__(self, name, index = None):
        self.name = name
        self.index = index