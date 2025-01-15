from sly import Lexer

class ImpLexer(Lexer):
    tokens = { PROGRAM, PROCEDURE, IS, BEGIN, END, IF, THEN, ELSE, ENDIF, WHILE, DO, ENDWHILE, REPEAT, UNTIL, FOR, FROM, TO, ENDFOR, DOWNTO, READ, WRITE, PIDENTIFIER, NUMBER, EQUAL, NOTEQUAL, GREATER, LESS, GREATEREQUAL, LESSEQUAL, PLUS, MINUS, MULTIPLY, DIVIDE, MOD, ASSIGN }

    literals = {'+', '-', '*', '/', '%', ',', ':', ';', '()', ')'}

    PROGRAM = r'PROGRAM'
    PROCEDURE = r'PROCEDURE'

    BEGIN = r'BEGIN'
    END = r'END'

    IS = r'IS'

    IF = r'IF'
    THEN = r'THEN'
    ELSE = r'ELSE'
    ENDIF = r'ENDIF'

    WHILE = r'WHILE'
    DO = r'DO'
    ENDWHILE = r'ENDWHILE'

    REPEAT = r'REPEAT'
    UNTIL = r'UNTIL'

    FOR = r'FOR'
    FROM = r'FROM'
    TO = r'TO'
    DOWNTO = r'DOWNTO'
    ENDFOR = r'ENDFOR'

    READ = r'READ'
    WRITE = r'WRITE'

    PIDENTIFIER = r'[_a-z]+'
    NUMBER = r'\d+'

    EQUAL = r'='
    NOTEQUAL = r'!='
    GREATER = r'>'
    LESS = r'<'
    GREATEREQUAL = r'>='
    LESSEQUAL = r'<='

    PLUS = r'\+'
    MINUS = r'\-'
    MULTIPLY = r'\*'
    DIVIDE = r'/'
    MOD = r'%'
    ASSIGN = r':='

    ignore = '[ \t\n]+'
    ignore_comment = r'#.*'

    def error(self, t):
        print(f"Nieznany znak: {t.value[0]}")
        self.index += 1
