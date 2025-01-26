from sly import Lexer

class MyLexer(Lexer):
    tokens = { "PROCEDURE", "ENDWHILE", "PROGRAM", "DOWNTO", "ENDFOR", "REPEAT", "BEGIN", "ENDIF", "UNTIL", "WHILE", "WRITE", "ELSE", "FROM", "THEN", "END", "FOR", "DO", "IF", "IS", "TO", "READ", "T", "PIDENTIFIER", "NUM", "ASSIGN", "NOTEQUAL", "GREATEREQUAL", "LESSEQUAL", "EQUAL", "GREATER", "LESS", "COMMA", "SEMICOLON", "COLON", "PLUS", "MINUS", "MULTIPLY", "DIVIDE", "MOD", "LBRACKET", "RBRACKET", "LPAREN", "RPAREN" }

    PROCEDURE = r'PROCEDURE'
    ENDWHILE = r'ENDWHILE'
    PROGRAM = r'PROGRAM'
    DOWNTO = r'DOWNTO'
    ENDFOR = r'ENDFOR'
    REPEAT = r'REPEAT'
    BEGIN  = r'BEGIN'
    ENDIF = r'ENDIF'
    UNTIL = r'UNTIL'
    WHILE = r'WHILE'
    WRITE = r'WRITE'
    ELSE = r'ELSE'
    FROM = r'FROM'
    READ = r'READ'
    THEN = r'THEN'
    END = r'END'
    FOR = r'FOR'
    DO = r'DO'
    IF = r'IF'
    IS = r'IS'
    TO = r'TO'

    ASSIGN = r':='
    NOTEQUAL = r'!='
    GREATEREQUAL = r'>='
    LESSEQUAL = r'<='
    EQUAL = r'='
    GREATER = r'>'
    LESS = r'<'
    COMMA = r','
    SEMICOLON = r';'
    COLON = r':'
    PLUS = r'\+'
    MINUS = r'\-'
    MULTIPLY = r'\*'
    DIVIDE = r'\/'
    MOD = r'\%'
    LBRACKET = r'\['
    RBRACKET = r'\]'
    LPAREN = r'\('
    RPAREN = r'\)'

    NUM = r'\d+'
    T = r'T'
    PIDENTIFIER = r'[_a-z]+'

    ignore = ' \t'

    @_(r'#.*')
    def ignore_comment(self, t):
        self.lineno += t.value.count('\n')

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    @_(r'\d+')
    def NUM(self, t):
        t.value = int(t.value)
        if self._is_in_range(t.value):
            return t
        else:
            raise Exception(f"Error: Value '{t.value}' not in range on line {self.lineno}")

    def error(self, t):
        raise Exception(f"Error: Unknown symbol: {t.value[0]} on line {self.lineno}")

    def _is_in_range(self, value):
        return value <= 2**63 - 1

    

if __name__ == '__main__':
    data0 = 'x := 3 + 42 * (s - t);'
    data1 = '''# Silnia+Fibonacci
    # ? 20
    # > 2432902008176640000
    # > 6765

    PROGRAM IS
        f[0:100], s[0:100], i[0:100], n
    BEGIN
        READ n;
        f[0] := 0;
        s[0] := 19;
    END
    '''

    lexer = MyLexer()
    for token in lexer.tokenize(data1):
        print(token)
