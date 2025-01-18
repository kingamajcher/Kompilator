from sly import Lexer

class MyLexer(Lexer):
    tokens = { PROGRAM, PROCEDURE, IS, BEGIN, END, IF, THEN, ELSE, ENDIF, WHILE, DO, ENDWHILE, REPEAT, UNTIL, FOR, FROM, TO, ENDFOR, DOWNTO, READ, WRITE, PIDENTIFIER, NUM, EQUAL, NOTEQUAL, GREATER, LESS, GREATEREQUAL, LESSEQUAL, PLUS, MINUS, MULTIPLY, DIVIDE, MOD, ASSIGN }

    literals = {'+', '-', '*', '/', '%', ',', ':', ';', '(', ')', '[', ']'}

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
    NUM = r'-?\d+'

    ASSIGN = r':='

    EQUAL = r'='
    NOTEQUAL = r'!='
    GREATER = r'>'
    LESS = r'<'
    GREATEREQUAL = r'>='
    LESSEQUAL = r'<='

    ignore = ' \t'

    @_(r'#.*')
    def ignore_comment(self, t):
        self.lineno += t.value.count('\n')  # Aktualizowanie linii

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')  # Aktualizowanie linii

    def NUM(self, t):
        t.value = int(t.value)  # Konwersja na liczbę
        return t

    def error(self, t):
        print(f"Nieznany znak: {t.value[0]!r} na linii {self.lineno}, kolumna {self.index}")
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
        #print('type=%r, value=%r' % (token.type, token.value))
