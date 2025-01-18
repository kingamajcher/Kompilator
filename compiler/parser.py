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
        return p[0] + [p[1]]

    @_('command')
    def commands(self, p):
        return [p[0]]


    # command
    @_('identifier ASSIGN expression SEMICOLON')
    def command(self, p):
        return "assign", p[0], p[2]

    @_('IF condition THEN commands ELSE commands ENDIF')
    def command(self, p):
        temp = "if_else", p[1], p[3], p[5], self.consts.copy() 
        self.consts.clear()
        return temp

    @_('IF condition THEN commands ENDIF')
    def command(self, p):
        temp = "if", p[1], p[3], self.consts.copy()
        self.consts.clear()
        return temp

    @_('WHILE condition DO commands ENDWHILE')
    def command(self, p):
        temp = "while", p[1], p[3], self.consts.copy()
        self.consts.clear()
        return temp

    @_('REPEAT commands UNTIL condition SEMICOLON')
    def command(self, p):
        temp = "repeat", p[3], p[1], self.consts.copy()
        self.consts.clear()
        return temp

    @_('FOR PIDENTIFIER FROM value TO value DO commands ENDFOR')
    def command(self, p):
        temp = "for_to", p[1], p[3], p[5], p[7], self.consts.copy()
        self.consts.clear()
        return temp

    @_('FOR PIDENTIFIER FROM value DOWNTO value DO commands ENDFOR')
    def command(self, p):
        temp = "for_downto", p[1], p[3], p[5], p[7], self.consts.copy()
        self.consts.clear()
        return temp

    @_('proc_call SEMICOLON')
    def command(self, p):
        pass

    @_('READ identifier SEMICOLON')
    def command(self, p):
        return "read", p[1]

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
        return p[0]

    @_('value PLUS value')
    def expression(self, p):
        return "add", p[0], p[2]

    @_('value MINUS value')
    def expression(self, p):
        return "sub", p[0], p[2]

    @_('value MULTIPLY value')
    def expression(self, p):
        return "mul", p[0], p[2]

    @_('value DIVIDE value')
    def expression(self, p):
        return "div", p[0], p[2]

    @_('value MOD value')
    def expression(self, p):
        return "mod", p[0], p[2]


    # condition
    @_('value EQUAL value')
    def condition(self, p):
        return "eq", p[0], p[2]

    @_('value NOTEQUAL value')
    def condition(self, p):
        return "neq", p[0], p[2]

    @_('value GREATER value')
    def condition(self, p):
        return "gt", p[0], p[2]

    @_('value LESS value')
    def condition(self, p):
        return "lt", p[0], p[2]

    @_('value GREATEREQUAL value')
    def condition(self, p):
        return "geq", p[0], p[2]

    @_('value LESSEQUAL value')
    def condition(self, p):
        return "leq", p[0], p[2]


    # value
    @_('NUM')
    def value(self, p):
        return "num", p[0]

    @_('identifier')
    def value(self, p):
        return "id", p[0]


    # identifier
    @_('PIDENTIFIER')
    def identifier(self, p):
        return "pid", p[0]

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