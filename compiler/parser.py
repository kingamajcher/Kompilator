from sly import Parser
from lexer import MyLexer
from symbol_table import SymbolTable, Variable, Iterator, Array
from code_generator import CodeGenerator

class MyParser(Parser):

    tokens = MyLexer.tokens
    symbol_table = SymbolTable()

    def __init__(self):
        super().__init__()
        self.generator = CodeGenerator(self.symbol_table)

    literal_constants = set()

    precedence = (
        ('left', 'PLUS', 'MINUS'), 
        ('left', 'MULTIPLY', 'DIVIDE', 'MOD') 
    )



    # Program
    @_('procedures main')
    def program_all(self, p):
        ast = ("program", p.procedures, p.main)
        print("\nAST:", ast)
        asm_code = self.generator.generate(ast)
        return asm_code


    # Procedures
    @_('procedures PROCEDURE proc_head IS declarations BEGIN commands END')
    def procedures(self, p):
        return p.procedures + [("procedure", p.proc_head, p.declarations, p.commands)]

    @_('procedures PROCEDURE proc_head IS BEGIN commands END')
    def procedures(self, p):
        return p.procedures + [("procedure", p.proc_head, [], p.commands)]

    @_('')
    def procedures(self, p):
        return []
    

    # Main function
    @_('PROGRAM IS declarations BEGIN commands END')
    def main(self, p):
        return "main", p.declarations, p.commands

    @_('PROGRAM IS BEGIN commands END')
    def main(self, p):
        return "main", [], p.commands


    # Commands list
    @_('commands command')
    def commands(self, p):
        return p.commands + [p.command]

    @_('command')
    def commands(self, p):
        return [p.command]


    # Single command
    @_('identifier ASSIGN expression SEMICOLON')
    def command(self, p):
        return "assign", p.identifier, p.expression

    @_('IF condition THEN commands ELSE commands ENDIF')
    def command(self, p):
        return "if_else", p.condition, p.commands0, p.commands1

    @_('IF condition THEN commands ENDIF')
    def command(self, p):
        return "if", p.condition, p.commands

    @_('WHILE condition DO commands ENDWHILE')
    def command(self, p):
        return "while", p.condition, p.commands

    @_('REPEAT commands UNTIL condition SEMICOLON')
    def command(self, p):
        return "repeat", p.commands, p.condition

    @_('FOR PIDENTIFIER FROM value TO value DO commands ENDFOR') 
    def command(self, p):
        return "for_to", p.PIDENTIFIER, p.value0, p.value1, p.commands

    @_('FOR PIDENTIFIER FROM value DOWNTO value DO commands ENDFOR')  
    def command(self, p):
        return "for_downto", p.PIDENTIFIER, p.value0, p.value1, p.commands
    
    @_('READ identifier SEMICOLON')
    def command(self, p):
        return "read", p.identifier

    @_('WRITE value SEMICOLON')
    def command(self, p):
        return "write", p.value

    @_('proc_call SEMICOLON')
    def command(self, p):
        return p.proc_call
    

    # Procedure header
    @_('PIDENTIFIER LPAREN args_decl RPAREN')
    def proc_head(self, p):
        return p.PIDENTIFIER, p.args_decl


    # Procedure call
    @_('PIDENTIFIER LPAREN args RPAREN')
    def proc_call(self, p):
        return "proc_call", p.PIDENTIFIER, p.args


    # Declarations
    @_('declarations COMMA PIDENTIFIER')
    def declarations(self, p):
        self.symbol_table.add_variable(p.PIDENTIFIER)
        return p.declarations + [("var", p.PIDENTIFIER)]

    @_('declarations COMMA PIDENTIFIER LBRACKET number COLON number RBRACKET')
    def declarations(self, p):
        self.symbol_table.add_array(p.PIDENTIFIER, p.number0, p.number1)
        return p.declarations + [("array", p.PIDENTIFIER, p.number0, p.number1)]

    @_('PIDENTIFIER')
    def declarations(self, p):
        self.symbol_table.add_variable(p.PIDENTIFIER)
        return [("var", p.PIDENTIFIER)]

    @_('PIDENTIFIER LBRACKET number COLON number RBRACKET')
    def declarations(self, p):
        self.symbol_table.add_array(p.PIDENTIFIER, p.number0, p.number1)
        return [("array", p.PIDENTIFIER, p.number0, p.number1)]


    # Arguments declarations
    @_('args_decl COMMA PIDENTIFIER')
    def args_decl(self, p):
        return p.args_decl + [p.PIDENTIFIER]

    @_('args_decl COMMA T PIDENTIFIER')
    def args_decl(self, p):
        return p.args_decl + [(p.T, p.PIDENTIFIER)]

    @_('PIDENTIFIER')
    def args_decl(self, p):
        return [p.PIDENTIFIER]

    @_('T PIDENTIFIER')
    def args_decl(self, p):
        return [(p.T, p.PIDENTIFIER)]


    # Arguments in procedure call
    @_('args COMMA PIDENTIFIER')
    def args(self, p):
        return p.args + [p.PIDENTIFIER]

    @_('PIDENTIFIER')
    def args(self, p):
        return [p.PIDENTIFIER]


    # Expressions
    @_('value')
    def expression(self, p):
        return p.value

    @_('value PLUS value')
    def expression(self, p):
        return "add", p.value0, p.value1

    @_('value MINUS value')
    def expression(self, p):
        return "substract", p.value0, p.value1

    @_('value MULTIPLY value')
    def expression(self, p):
        return "multiply", p.value0, p.value1

    @_('value DIVIDE value')
    def expression(self, p):
        return "divide", p.value0, p.value1

    @_('value MOD value')
    def expression(self, p):
        return "mod", p.value0, p.value1


    # Conditions
    @_('value EQUAL value')
    def condition(self, p):
        return "equal", p.value0, p.value1

    @_('value NOTEQUAL value')
    def condition(self, p):
        return "notequal", p.value0, p.value1

    @_('value GREATER value')
    def condition(self, p):
        return "greater", p.value0, p.value1

    @_('value LESS value')
    def condition(self, p):
        return "less", p.value0, p.value1

    @_('value GREATEREQUAL value')
    def condition(self, p):
        return "greaterequal", p.value0, p.value1

    @_('value LESSEQUAL value')
    def condition(self, p):
        return "lessequal", p.value0, p.value1


    # Numbers
    @_('NUM')
    def number(self, p):
        return p.NUM

    @_('MINUS NUM')
    def number(self, p):
        return -(p.NUM)
    

    # Values
    @_('number')
    def value(self, p):
        return "num", p.number

    @_('identifier')
    def value(self, p):
        return "id", p.identifier


    # identifier
    @_('PIDENTIFIER')
    def identifier(self, p):
        if p.PIDENTIFIER in self.symbol_table or p.PIDENTIFIER in self.symbol_table.iterators:
            return p.PIDENTIFIER
        else:
            return "other", p.PIDENTIFIER

    @_('PIDENTIFIER LBRACKET PIDENTIFIER RBRACKET')
    def identifier(self, p):
        if p.PIDENTIFIER1 in self.symbol_table and type(self.symbol_table[p.PIDENTIFIER1]) == Variable:
            return "array", p.PIDENTIFIER0, ("id", p.PIDENTIFIER1)
        else:
            return "array", p.PIDENTIFIER0, ("id", ("other", p.PIDENTIFIER1))

    @_('PIDENTIFIER LBRACKET number RBRACKET')
    def identifier(self, p):
        return "array", p.PIDENTIFIER, p.number

    # -----------------------------------------------
    def error(self, p):
        if p:
            print(f'Syntax error: {p.type} on line {p.lineno}.')
        else:
            print("Syntax error at EOF.")
