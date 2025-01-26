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
    T = r'T'

    PIDENTIFIER = r'[_a-z]+'

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

    ignore = ' \t'

    @_(r'#.*')
    def ignore_comment(self, t):
        self.lineno += t.value.count('\n')

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    def NUM(self, t):
        t.value = int(t.value)
        return t

    def error(self, t):
        print(f"Unknown symbol: {t.value[0]!r} on line {self.lineno}")
        self.index += 1

    

if __name__ == '__main__':
    data0 = 'x := 3 + 42 * (s - t);'
    data1 = '''# Silnia+Fibonacci
    # ? 20
    # > 2432902008176640000
    # > 6765

    PROGRAM IS
        f[0:100], s[0:100], i[0:100], n, j, k, l
    BEGIN
        READ n;
        f[0] := 0;
        s[0] := 1;
        i[0] := 0;
        f[1] := 1;
        s[1] := 1;
        i[1] := 1;
        FOR j FROM 2 TO n DO
            k := j - 1;
            l := k - 1;
        i[j] := i[k] + 1;
        f[j] := f[k] + f[l];
            s[j] := s[k] * i[j];
        ENDFOR
        WRITE s[n];
        WRITE f[n];
    END
    '''

    lexer = MyLexer()
    for token in lexer.tokenize(data1):
        print(token)
