from sly import Parser
from lexer import MyLexer
from symbol_table import SymbolTable
from ast_tree import *

class MyParser(Parser):
    tokens = MyLexer.tokens
    symbol_table = SymbolTable()
    current_scope = None

    precedence = (
        ('left', 'PLUS', 'MINUS'),
        ('left', 'MULTIPLY', 'DIVIDE', 'MOD')
    )

    # Program
    @_('procedures main')
    def program_all(self, p):
        return AST(Program(p.procedures, p.main))


    # Procedures
    @_('procedures PROCEDURE proc_head IS declarations BEGIN commands END')
    def procedures(self, p):
        name, parameters = p.proc_head
        try:
            procedure_scope = self.symbol_table.add_procedure(name, parameters)
            self.current_scope = procedure_scope  # Przełącz na lokalny zakres procedury
            for declaration in p.declarations:
                if isinstance(declaration, Declaration):
                    if declaration.is_array:
                        self.symbol_table.add_array(declaration.name, *declaration.bounds, self.current_scope)
                    else:
                        self.symbol_table.add_variable(declaration.name, self.current_scope)
            commands = p.commands
            self.current_scope = None  # Powrót do globalnego zakresu
        except Exception as e:
            print(f"Error while adding procedure '{name}': {e}")
        return Procedures(p.procedures.procedures + [Procedure(name, parameters, p.declarations, p.commands)])

    @_('procedures PROCEDURE proc_head IS BEGIN commands END')
    def procedures(self, p):
        name, parameters = p.proc_head
        # Dodaj procedurę do globalnej tablicy symboli
        procedure_scope = self.symbol_table.add_procedure(name, parameters)
        self.current_scope = procedure_scope.locals  # Przełącz na lokalny zakres procedury
        commands = p.commands
        self.current_scope = None  # Powrót do globalnego zakresu
        return Procedures(p.procedures.procedures + [Procedure(name, parameters, [], commands)])

    @_('')
    def procedures(self, p):
        return Procedures()


    # Main function
    @_('PROGRAM IS declarations BEGIN commands END')
    def main(self, p):
        return Main(p.declarations, p.commands)

    @_('PROGRAM IS BEGIN commands END')
    def main(self, p):
        return Main([], p.commands)


    # Commands list
    @_('commands command')
    def commands(self, p):
        return Commands(p.commands.commands + [p.command])

    @_('command')
    def commands(self, p):
        return Commands([p.command])


    # Single command
    @_('identifier ASSIGN expression SEMICOLON')
    def command(self, p):
        return Assign(p.identifier, p.expression)

    @_('IF condition THEN commands ELSE commands ENDIF')
    def command(self, p):
        return If(p.condition, p.commands0, p.commands1)

    @_('IF condition THEN commands ENDIF')
    def command(self, p):
        return If(p.condition, p.commands)

    @_('WHILE condition DO commands ENDWHILE')
    def command(self, p):
        return While(p.condition, p.commands)

    @_('REPEAT commands UNTIL condition SEMICOLON')
    def command(self, p):
        return RepeatUntil(p.commands, p.condition)

    @_('FOR PIDENTIFIER FROM value TO value DO commands ENDFOR')
    def command(self, p):
        return For(p.PIDENTIFIER, p.value0, p.value1, "to", p.commands)

    @_('FOR PIDENTIFIER FROM value DOWNTO value DO commands ENDFOR')
    def command(self, p):
        return For(p.PIDENTIFIER, p.value0, p.value1, "downto", p.commands)

    @_('READ identifier SEMICOLON')
    def command(self, p):
        return Read(p.identifier)

    @_('WRITE value SEMICOLON')
    def command(self, p):
        return Write(p.value)

    @_('proc_call SEMICOLON')
    def command(self, p):
        return p.proc_call


    # Procedure header
    @_('PIDENTIFIER LPAREN args_decl RPAREN')
    def proc_head(self, p):
        return (p.PIDENTIFIER, p.args_decl)


    # Procedure call
    @_('PIDENTIFIER LPAREN args RPAREN')
    def proc_call(self, p):
        return ProcCall(p.PIDENTIFIER, p.args)


    # Declarations
    @_('declarations COMMA PIDENTIFIER')
    def declarations(self, p):
        if self.current_scope:  # Jeśli jesteśmy w procedurze
            self.current_scope.add_variable(p.PIDENTIFIER)
        else:  # Jeśli jesteśmy w zakresie globalnym
            self.symbol_table.add_variable(p.PIDENTIFIER)
        return p.declarations + [Declaration(p.PIDENTIFIER)]

    @_('declarations COMMA PIDENTIFIER LBRACKET NUM COLON NUM RBRACKET')
    def declarations(self, p):
        try:
            if self.current_scope:  # Jeśli jesteśmy w procedurze
                self.symbol_table.add_array(p.PIDENTIFIER, p.NUM, p.NUM1, self.current_scope)
            else:  # Jeśli jesteśmy w zakresie globalnym
                self.symbol_table.add_array(p.PIDENTIFIER, p.NUM, p.NUM1)
        except Exception as e:
            print(f"Error: {e}")
        return p.declarations + [Declaration(p.PIDENTIFIER, (p.NUM, p.NUM1))]

    @_('PIDENTIFIER')
    def declarations(self, p):
        if self.current_scope:
            self.current_scope.add_variable(p.PIDENTIFIER)
        else:
            self.symbol_table.add_variable(p.PIDENTIFIER)
        return [Declaration(p.PIDENTIFIER)]

    @_('PIDENTIFIER LBRACKET NUM COLON NUM RBRACKET')
    def declarations(self, p):
        try:
            if self.current_scope:
                self.symbol_table.add_array(p.PIDENTIFIER, p.NUM, p.NUM1, self.current_scope)
            else:
                self.symbol_table.add_array(p.PIDENTIFIER, p.NUM, p.NUM1)
        except Exception as e:
            print(f"Error: {e}")
        return [Declaration(p.PIDENTIFIER, (p.NUM, p.NUM1))]


    # Arguments declarations
    @_('args_decl COMMA PIDENTIFIER')
    def args_decl(self, p):
        return p.args_decl + [p.PIDENTIFIER]

    @_('args_decl COMMA T PIDENTIFIER')
    def args_decl(self, p):
        return p.args_decl + [(p.PIDENTIFIER, "table")]

    @_('PIDENTIFIER')
    def args_decl(self, p):
        return [p.PIDENTIFIER]

    @_('T PIDENTIFIER')
    def args_decl(self, p):
        return [(p.PIDENTIFIER, "table")]


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
        return Operation(p.value0, '+', p.value1)

    @_('value MINUS value')
    def expression(self, p):
        return Operation(p.value0, '-', p.value1)

    @_('value MULTIPLY value')
    def expression(self, p):
        return Operation(p.value0, '*', p.value1)

    @_('value DIVIDE value')
    def expression(self, p):
        return Operation(p.value0, '/', p.value1)

    @_('value MOD value')
    def expression(self, p):
        return Operation(p.value0, '%', p.value1)


    # Conditions
    @_('value EQUAL value')
    def condition(self, p):
        return Condition(p.value0, '==', p.value1)

    @_('value NOTEQUAL value')
    def condition(self, p):
        return Condition(p.value0, '!=', p.value1)

    @_('value GREATER value')
    def condition(self, p):
        return Condition(p.value0, '>', p.value1)

    @_('value LESS value')
    def condition(self, p):
        return Condition(p.value0, '<', p.value1)

    @_('value GREATEREQUAL value')
    def condition(self, p):
        return Condition(p.value0, '>=', p.value1)

    @_('value LESSEQUAL value')
    def condition(self, p):
        return Condition(p.value0, '<=', p.value1)


    # Values
    @_('NUM')
    def value(self, p):
        return Value(p.NUM)

    @_('identifier')
    def value(self, p):
        return p.identifier


    # Identifiers
    @_('PIDENTIFIER')
    def identifier(self, p):
        return Identifier(p.PIDENTIFIER)

    @_('PIDENTIFIER LBRACKET NUM RBRACKET')
    def identifier(self, p):
        return Identifier(p.PIDENTIFIER, Value(p.NUM))

    @_('PIDENTIFIER LBRACKET PIDENTIFIER RBRACKET')
    def identifier(self, p):
        return Identifier(p.PIDENTIFIER0, Identifier(p.PIDENTIFIER1))


    # Error handling
    def error(self, p):
        if p:
            print(f"Syntax error at token {p.type} ({p.value}) on line {p.lineno}")
        else:
            print("Syntax error at EOF")