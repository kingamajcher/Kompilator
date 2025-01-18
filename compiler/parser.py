from sly import Parser

from lexer import MyLexer

class MyParser(Parser):
    tokens = MyLexer.tokens

    precedence = (
        ('left', 'PLUS', 'MINUS'),
        ('left', 'MULTIPLY', 'DIVIDE', 'MOD')
    )

    # program_all
    @_('procedures main')
    def program_all(self, p):
        pass


    # procedures
    @_('procedures PROCEDURE proc_head IS declarations BEGIN commands END')
    def procedures(self, p):
        pass

    @_('procedures PROCEDURE proc_head IS BEGIN commands END')
    def procedures(self, p):
        pass

    @_('')
    def procedures(self, p):
        pass


    # main
    @_('PROGRAM IS declarations BEGIN commands END')
    def main(self, p):
        pass

    @_('PROGRAM IS BEGIN commands END')
    def main(self, p):
        pass


    # commands
    @_('commands command')
    def commands(self, p):
        pass

    @_('command')
    def commands(self, p):
        pass


    # command
    @_('identifier ASSIGN expression SEMICOLON')
    def command(self, p):
        pass

    @_('IF condition THEN commands ELSE commands ENDIF')
    def command(self, p):
        pass

    @_('IF condition THEN commands ENDIF')
    def command(self, p):
        pass

    @_('WHILE condition DO commands ENDWHILE')
    def command(self, p):
        pass

    @_('REPEAT commands UNTIL condition SEMICOLON')
    def command(self, p):
        pass

    @_('FOR PIDENTIFIER FROM value TO value DO commands ENDFOR')
    def command(self, p):
        pass

    @_('FOR PIDENTIFIER FROM value DOWNTO value DO commands ENDFOR')
    def command(self, p):
        pass

    @_('proc_call SEMICOLON')
    def command(self, p):
        pass

    @_('READ identifier SEMICOLON')
    def command(self, p):
        pass

    @_('WRITE value SEMICOLON')
    def command(self, p):
        pass


    # proc_head
    @_('PIDENTIFIER LPAREN args_decl RPAREN')
    def proc_head(self, p):
        pass


    # proc_call
    @_('PIDENTIFIER LPAREN args RPAREN')
    def proc_call(self, p):
        pass


    # declarations
    @_('declarations COMMA PIDENTIFIER')
    def declarations(self, p):
        pass

    @_('declarations COMMA PIDENTIFIER LBRACKET NUM COLON NUM RBRACKET')
    def declarations(self, p):
        pass

    @_('PIDENTIFIER')
    def declarations(self, p):
        pass

    @_('PIDENTIFIER LBRACKET NUM COLON NUM RBRACKET')
    def declarations(self, p):
        pass


    # args_decl
    @_('args_decl COMMA PIDENTIFIER')
    def args_decl(self, p):
        pass

    @_('args_decl COMMA T PIDENTIFIER')
    def args_decl(self, p):
        pass

    @_('PIDENTIFIER')
    def args_decl(self, p):
        pass

    @_('T PIDENTIFIER')
    def args_decl(self, p):
        pass


    # args
    @_('args COMMA PIDENTIFIER')
    def args(self, p):
        pass

    @_('PIDENTIFIER')
    def args(self, p):
        pass


    # expression
    @_('value')
    def expression(self, p):
        pass

    @_('value PLUS value')
    def expression(self, p):
        pass

    @_('value MINUS value')
    def expression(self, p):
        pass

    @_('value MULTIPLY value')
    def expression(self, p):
        pass

    @_('value DIVIDE value')
    def expression(self, p):
        pass

    @_('value MOD value')
    def expression(self, p):
        pass


    # condition
    @_('value EQUAL value')
    def condition(self, p):
        pass

    @_('value NOTEQUAL value')
    def condition(self, p):
        pass

    @_('value GREATER value')
    def condition(self, p):
        pass

    @_('value LESS value')
    def condition(self, p):
        pass

    @_('value GREATEREQUAL value')
    def condition(self, p):
        pass

    @_('value LESSEQUAL value')
    def condition(self, p):
        pass


    # value
    @_('NUM')
    def value(self, p):
        pass

    @_('identifier')
    def value(self, p):
        pass


    # identifier
    @_('PIDENTIFIER')
    def identifier(self, p):
        pass

    @_('PIDENTIFIER LBRACKET PIDENTIFIER RBRACKET')
    def identifier(self, p):
        pass

    @_('PIDENTIFIER LBRACKET NUM RBRACKET')
    def identifier(self, p):
        pass


    # error
    def error(self, p):
        if p:
            print(f'Syntax error: {p.type}')
        else:
            print("Syntax error at EOF")