from symbol_table import *

class CodeGenerator:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.code = []

    def generate(self, ast):
        if ast[0] == 'program':
            _, procedures, main = ast
            self.generate_code_procedures(procedures)
            self.generate_code_main(main)
            self.code.append("HALT")
        return "\n".join(self.code)
    
    def generate_code_procedures(self, procedures):
        for proc in procedures:
            if proc[0] == "procedure":
                self.generate_code_procedure(proc)

    def generate_code_procedure(self, proc):
        _, proc_head, declarations, commands = proc
        proc_name, params = proc_head
        pass

    def generate_code_main(self, main):
        _, declarations, commands = main
        self.generate_code_commands(commands)

    def generate_code_commands(self, commands):
        for command in commands:
            self.generate_code_command(command)

    def generate_code_command(self, command):
        if command[0] == "assign":
            _, identifier, expression = command
            self.assign(identifier, expression)
        elif command[0] == "if_else":
            _, condition, true_commands, false_commands, constants = command
        elif command[0] == "if":
            _, condition, true_commands, constants = command
        elif command[0] == 'while':
            _, condition, commands, constants = command
        elif command[0] == "repeat":
            _, commands, condition, constants = command
        elif command[0] == "for_to":
            _, iterator, start_value, end_value, commands, constants = command
        elif command[0] == "for_downto":
            _, iterator, start_value, end_value, commands, constants = command
        elif command[0] == "read":
            _, identifier = command
            self.read(identifier)
        elif command[0] == "write":
            _, value = command
            self.write(value)
        elif command[0] == "proc_call":
            _, proc_name, args = command



    def generate_code_expression(self, expression):
        if expression[0] == "num":
            self.code.append(f"SET {expression[1]}")
        elif expression[0] == "id":
            self.expression_id(expression[1])
        elif expression[0] == "plus":
            self.add(expression)
        elif expression[0] == "minus":
            self.substract(expression)
        elif expression[0] == "multiply":
            pass
        elif expression[0] == "divide":
            self.divide(expression)
        elif expression[0] == "mod":
            pass
        else:
            raise Exception(f"Error: Invalid expression type '{expression[0]}'")

    def expression_id(self, expr):
        # handling of undeclared variables
        if expr[0] == "undeclared":
            if expr[1] in self.symbol_table.iterators:
                iterator_addr = self.symbol_table.get_iterator(expr[1])
                self.code.append(f"LOAD {iterator_addr}")
            else:
                raise Exception(f"Error: undeclared variable '{expr[1]}'")
        # handling of array indices
        elif expr[0] == "array":
            name = expr[1]
            index = expr[2]

            # tu cos bedzie ale mi sie nie chce
        # handling of variables
        elif isinstance(expr[0], str):
            name = expr[0]
            if name in self.symbol_table:
                address = self.symbol_table.get_address(name)
                self.code.append(f"LOAD {address}")
            else:
                raise Exception("Error: unknown variable '{name}'")
        else:
            raise Exception("Error: wrong expression id format")
        
    def assign(self, variable, expression):
        if isinstance(variable, tuple):
            if variable[0] == "undeclared":
                if variable[1] in self.symbol_table.iterators:
                    raise Exception(f"Error: cannot assign value to iterator '{variable[1]}'")
                else:
                    raise Exception(f"Error: Undeclared variable '{variable[1]}'")
            elif variable[0] == "array":
                name = variable[1]
                index = variable[2]
                address = self.array_index(name, index)
                self.generate_code_expression(expression)
                if (address != 0):
                    self.code.append(f"STORE {address}")
                else:
                    self.code.append(f'STOREI 1')
        else:
            if isinstance(variable, str):
                self.symbol_table[variable].initialized = True
                address = self.symbol_table.get_address(variable)
                self.generate_code_expression(expression)
                self.code.append(f"STORE {address}")
            else:
                raise Exception(f"Error: Assigning to invalid type")
    
    def write(self, value):
        if value[0] == "id":
            if isinstance(value[1], tuple):
                pass
            else:
                variable = self.symbol_table.get_address(value[1])
                self.code.append(f"PUT {variable}")
        elif value[0] == "num":
            self.code.append(f"SET {value[1]}")
            self.code.append(f"PUT 0")
        else:
            raise Exception(f"Error: invalid value type '{value[0]}' for WRITE")

    def read(self, identifier):
        if isinstance(identifier, tuple):
            #tablice i undeclared
            #to sie kiedys dorobi xd
            pass
        else:
            if identifier in self.symbol_table:
                self.symbol_table[identifier].initialized = True
                address = self.symbol_table.get_address(identifier)
            # może trzeba pomyślec nad obsługa iteratorów bo ich chyba nie można read
            self.code.append(f"GET {address}")

    def add(self, expression):
        self.generate_code_expression(expression[1])
        self.code.append("STORE 1")
        self.generate_code_expression(expression[2])
        self.code.append("ADD 1")

    def substract(self, expression):
        self.generate_code_expression(expression[2])
        self.code.append("STORE 1")
        self.generate_code_expression(expression[1])
        self.code.append("SUB 1")

    def multiply(self, expression):
        pass

    def divide(self, expression):
        dividend = expression[1] # a
        divisor = expression[2] # b

        print(dividend[0])
        print(divisor[0])
        if divisor[0] == "num" and divisor[1] == 0:
            self.code.append("SET 0")
        elif dividend[0] == "num" and dividend[1] == 0:
            self.code.append("SET 0")
        elif dividend[0] == "num" and divisor[0] == "num":
            result = dividend[1] // divisor[1]
            self.code.append(f"SET {result}")
        else:
            # p1 -> abs(a)
            # p2 -> abs(b)
            # p3 -> sign(a)
            # p4 -> sign(b)
            # p5 -> wynik
            # p6 -> k
            # p7 -> pomocnicze abs(a)
            # p8 -> pomocnicze abs(b)
            # p9 -> pomocnicze (nie ważne co tam jest)

            # znaki dzielonych wartości
            self.code.append("SET 0")
            self.code.append("STORE 3")
            self.code.append("STORE 4")

            # wynik (na razie ma być 0)
            self.code.append("STORE 5")

            # k
            self.code.append("SET 1")
            self.code.append("STORE 6")
            self.code.append("STORE 9")

            # ładujemy dzielną
            self.generate_code_expression(dividend)

            # jesli jest zerem to dziki skok na koniec zeby zwracalo od razu zero
            self.code.append("JZERO 80")

            # jesli niedodatnie to wykona, jeśli dodatnie to skoczy o 6
            self.code.append("JPOS 6")

            # ustawiamy wartość dzielnej
            self.code.append("STORE 1")

            # ustawiamy znak pierwszej liczby
            self.code.append("SET 1")
            self.code.append("STORE 3")

            # zmieniamy znak aby było dodatnie
            self.code.append("SET 0")
            self.code.append("SUB 1")
            self.code.append("STORE 1")

            # zapisujemy pomocnicze |a|
            self.code.append("STORE 7")
            
            # ładujemy dzielnik
            self.generate_code_expression(divisor)

            # jesli jest 0 to dziki jump do konca i zwraca 0
            self.code.append("JZERO 70")

            # jesli jest 1 to dziki jump i zwraca dzielną
            self.code.append("STORE 2")
            
            self.code.append("SUB 9")
            self.code.append("JZERO 2")
            self.code.append("JUMP 10")
            self.code.append("LOAD 3")
            self.code.append("JZERO 5")
            self.code.append("LOAD 5")
            self.code.append("SUB 1")
            self.code.append("STORE 5")
            self.code.append("JUMP 3")
            self.code.append("LOAD 1")
            self.code.append("STORE 5")
            self.code.append("JUMP 57")

            # jesli jest 2 to dziki jump do robienia half i zwraca wartośc

            # jesli niedodatnie to wykona, jeśli dodatnie to skoczy o 6
            self.code.append("LOAD 2")
            self.code.append("JPOS 6")

            # ustawiamy wartość dzielnika 
            self.code.append("STORE 2")

            # ustawiamy znak dzielnika
            self.code.append("SET -1")
            self.code.append("STORE 4")

            # zmieniamy znak aby było dodatnie
            self.code.append("SET 0")
            self.code.append("SUB 2")
            self.code.append("STORE 2")

            # zapisujemy pomocnicze |b|
            self.code.append("STORE 8")

            # pierwsza pętla

            # załaduj |a| pomocnicze
            self.code.append("LOAD 7")
            
            # odejmnij b
            self.code.append("SUB 8")

            # poskakaj sobie
            self.code.append("JPOS 3")
            self.code.append("JZERO 2")
            self.code.append("JUMP 8")

            # dodaj b do k 
            self.code.append("LOAD 8")
            self.code.append("ADD 8")
            self.code.append("STORE 8")
            self.code.append("LOAD 6")
            self.code.append("ADD 6")
            self.code.append("STORE 6")
            self.code.append("JUMP -11")

            # dzielimy sobie przez 2
            self.code.append("LOAD 8")
            self.code.append("HALF")
            self.code.append("STORE 8")
            self.code.append("LOAD 6")
            self.code.append("HALF")
            self.code.append("STORE 6")

            # pętla z mod
            self.code.append("LOAD 7")
            self.code.append("SUB 2")
            self.code.append("JPOS 3")
            self.code.append("JZERO 2")
            self.code.append("JUMP 19")

            self.code.append("LOAD 7")
            self.code.append("SUB 8")
            self.code.append("JPOS 3")
            self.code.append("JZERO 2")
            self.code.append("JUMP 7")

            self.code.append("LOAD 7")
            self.code.append("SUB 8")
            self.code.append("STORE 7")

            # ładujemy do wyniku
            self.code.append("LOAD 5")

            self.code.append("ADD 6")
            self.code.append("STORE 5")

            # dzielimy przez 2
            self.code.append("LOAD 8")
            self.code.append("HALF")
            self.code.append("STORE 8")
            self.code.append("LOAD 6")
            self.code.append("HALF")
            self.code.append("STORE 6")

            self.code.append("JUMP -22")

            # sprawdzanie znaku
            self.code.append("LOAD 3")
            self.code.append("ADD 4")
            self.code.append("JZERO 4")

            # zmiana znaku jeśli jest taka potrzeba
            self.code.append("SET 0")
            self.code.append("SUB 5")
            self.code.append("STORE 5")

            self.code.append("LOAD 5")


    def modulo(self, expression):
        pass

