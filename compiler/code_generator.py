from symbol_table import *

class CodeGenerator:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.code = []
        self.iterators = []
        self.current_procedure = None

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
            self.generate_code_assign(identifier, expression)
        elif command[0] == "if_else":
            _, condition, true_commands, false_commands, constants = command
            self.generate_code_if_else(condition, true_commands, false_commands)
        elif command[0] == "if":
            _, condition, true_commands, constants = command
            self.generate_code_if(condition, true_commands)
        elif command[0] == 'while':
            _, condition, commands, constants = command
            self.generate_code_while(condition, commands)
        elif command[0] == "repeat":
            _, commands, condition, constants = command
            self.generate_code_repeat(commands, condition)
        elif command[0] == "for_to":
            _, iterator, start_value, end_value, commands, constants = command
            self.generate_code_for(iterator, start_value, end_value, commands, False)
        elif command[0] == "for_downto":
            _, iterator, start_value, end_value, commands, constants = command
            self.generate_code_for(iterator, start_value, end_value, commands, True)
        elif command[0] == "read":
            _, identifier = command
            self.generate_code_read(identifier)
        elif command[0] == "write":
            _, value = command
            self.generate_code_write(value)
        elif command[0] == "proc_call":
            _, proc_name, args = command
            self.generate_code_proc_call(proc_name, args)



    def generate_code_expression(self, expression):
        expression_type = expression[0]
        if expression_type == "num":
            value = expression[1]
            self.code.append(f"SET {value}")
        elif expression_type == "id":
            identifier = expression[1]
            self.handle_identifier(identifier)
        elif expression_type == "add":
            self.add(expression)
        elif expression_type == "substract":
            self.substract(expression)
        elif expression_type == "multiply":
            self.multiply(expression)
        elif expression_type == "divide":
            self.divide(expression)
        elif expression_type == "mod":
            self.modulo(expression)
        else:
            raise Exception(f"Error: Invalid expression type '{expression_type}'")

    def handle_identifier(self, expression):
        # handling of undeclared variables
        if expression[0] == "undeclared":
            if expression[1] in self.symbol_table.iterators:
                iterator_address = self.symbol_table.get_iterator(expression[1])
                self.code.append(f"LOAD {iterator_address}")
            else:
                raise Exception(f"Error: undeclared variable '{expression[1]}'")
        # handling of array indices
        elif expression[0] == "array":
            name = expression[1]
            index = expression[2]

            address = self.handle_array_at_index(name, index)

            if address == 0:
                self.code.append(f"LOADI 1")
            else:
                self.code.append(f"LOAD {address}")


        # handling of variables
        elif isinstance(expression[0], str):
            name = expression[0]
            if name in self.symbol_table:
                address = self.symbol_table.get_address(name)
                self.code.append(f"LOAD {address}")
            else:
                raise Exception(f"Error: unknown variable '{name}'")
        else:
            raise Exception("Error: wrong expression id format")
        
    def generate_code_assign(self, variable, expression):
        if isinstance(variable, tuple):
            if variable[0] == "undeclared":
                if variable[1] in self.symbol_table.iterators:
                    raise Exception(f"Error: Cannot assign value to iterator '{variable[1]}'")
                else:
                    raise Exception(f"Error: Undeclared variable '{variable[1]}'")
            elif variable[0] == "array":
                name = variable[1]
                index = variable[2]
                address = self.handle_array_at_index(name, index)
                self.generate_code_expression(expression)
                if address != 0:
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
            
    def generate_code_if_else(self, condition, true_commands, false_commands):
        simplified_condition = self.simplify_condition_if_possible(condition)
        if simplified_condition == True:
                self.generate_code_commands(true_commands)
        elif simplified_condition == False:
                self.generate_code_commands(false_commands)
        else:
            condition_start = len(self.code)
            self.generate_condition_jumps(simplified_condition)
            true_commands_start = len(self.code)
            self.generate_code_commands(true_commands)
            self.code.append("JUMP end")
            false_commands_start = len(self.code)
            self.generate_code_commands(false_commands)
            end_of_if = len(self.code)
            end = str(end_of_if - false_commands_start + 1)
            self.code[false_commands_start - 1] = f"JUMP {end}"
            for i in range(condition_start, true_commands_start):
                end = str(false_commands_start - i)
                if self.code[i] == "JUMP end":
                    self.code[i] = f"JUMP {end}"


    def generate_code_if(self, condition, true_commands):
        simplified_condition = self.simplify_condition_if_possible(condition)
        if simplified_condition == True:
            self.generate_code_commands(true_commands)
        elif simplified_condition == False:
            pass
        else:
            condition_start = len(self.code)
            self.generate_condition_jumps(simplified_condition)
            command_start = len(self.code)
            self.generate_code_commands(true_commands)
            command_end = len(self.code)
            for i in range(condition_start, command_start):
                end = str(command_end - i)
                if self.code[i] == "JUMP end":
                    self.code[i] = f"JUMP {end}"


    def generate_code_while(self, condition, commands):
        simplified_condition = self.simplify_condition_if_possible(condition)
        if simplified_condition == True:
            raise Exception("Error: Infinite loop")
        elif simplified_condition == False:
            pass
        else:
            condition_start = len(self.code)
            self.generate_condition_jumps(simplified_condition)
            loop_start = len(self.code)
            self.generate_code_commands(commands)
            jump = condition_start - len(self.code)
            self.code.append(f"JUMP {jump}")
            loop_end = len(self.code)
            for i in range(condition_start, loop_start):
                end = str(loop_end - i)
                if self.code[i] == "JUMP end":
                    self.code[i] = f"JUMP {end}"

    def generate_code_repeat(self, commands, condition):
        simplified_condition = self.simplify_condition_if_possible(condition)
        if simplified_condition == True:
            self.generate_code_commands(commands)
        elif simplified_condition == False:
            raise Exception("Error: Infinite loop")
        else:
            loop_start = len(self.code)
            self.generate_code_commands(commands)
            condition_start = len(self.code)
            self.generate_condition_jumps(simplified_condition)
            loop_end = len(self.code)
            for i in range(condition_start, loop_end):
                if self.code[i] == "JUMP end":
                    self.code[i] = f"JUMP 2"
            self.code.append(f"JUMP 2")
            jump = str(-(loop_end - loop_start + 1))
            self.code.append(f"JUMP {jump}")


    def generate_code_for(self, iterator, start_value, end_value, commands, downto):
        if start_value[0] == "num" and end_value[0] == "num":
            if downto:
                if start_value[1] > end_value[1]:
                    raise Exception("Error: Invalid range for loop")
            else:
                if start_value[1] < end_value[1]:
                    raise Exception("Error: Invalid range for loop")
                
        if iterator in self.symbol_table:
            raise Exception(f"Error: Redeclaration of iterator '{iterator}'")
        
        if self.iterators:
            address, limit_address = self.symbol_table.get_iterator(self.iterators[-1])
            self.code.append(f"STORE {address}")
        else:
            pass

        
        
    
    def generate_code_write(self, value):
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

    def generate_code_read(self, identifier):
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

    def generate_code_proc_call(self, proc_name, args):
        pass

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
        # a * b
        a = expression[1]
        b = expression[2]

        if a[0] == "num" and b[0] == "num":
            result = a[1] * b[1]
            self.code.append(f"SET {result}")
        else:
            # p1 -> abs(a)
            # p2 -> abs(b)
            # p3 -> sign(a)
            # p4 -> sign(b)
            # p5 -> wynik
            # p6 -> pomocnicze b do sprawdzania nieparzystości

            # znaki mnożonych wartości i wynik wstępnie ujstawiony na 0
            self.code.append("SUB 0")
            self.code.append("STORE 5")
            
            # ładujemy a
            self.generate_code_expression(a)

            # jesli ujemna to zmiana flagi znaku i wartosc bezwgledna
            self.code.append("JPOS 6")
            self.code.append("STORE 1")
            self.code.append("SET 1")
            self.code.append("STORE 3")

            self.code.append("SUB 0")
            self.code.append("SUB 1")
            self.code.append("STORE 1")

            # ładujemy b
            self.generate_code_expression(b)

            # jesli ujemna to zmiana flagi znaku i wartosc bezwgledna
            self.code.append("JPOS 6")
            self.code.append("STORE 2")
            self.code.append("SET -1")
            self.code.append("STORE 4")

            self.code.append("SUB 0")
            self.code.append("SUB 2")
            self.code.append("STORE 2")

            #sprawdzanie czy sa zerami, jak tak to konczymy
            self.code.append("LOAD 1")
            self.code.append("JZERO 25")
            self.code.append("LOAD 2")
            self.code.append("JZERO 23")

            # mnozenie

            # sprawdzmy czy b jest nieparzyste
            self.code.append("LOAD 2")
            self.code.append("HALF")
            self.code.append("STORE 6")

            self.code.append("ADD 0")
            self.code.append("SUB 2")
            self.code.append("JZERO 4")

            # dodaj a do wyniku
            self.code.append("LOAD 5")
            self.code.append("ADD 1")
            self.code.append("STORE 5")

            # a = a*2
            self.code.append("LOAD 1")
            self.code.append("ADD 0")
            self.code.append("STORE 1")

            # b = b/2
            self.code.append("LOAD 2")
            self.code.append("HALF")
            self.code.append("STORE 2")

            self.code.append("JPOS -15")

            # zmiana znaku jesli potrzebna
            self.code.append("LOAD 3")
            self.code.append("ADD 4")
            self.code.append("JZERO 4")

            self.code.append("SUB 0")
            self.code.append("SUB 5")
            self.code.append("STORE 5")

            self.code.append("LOAD 5")


    def divide(self, expression):
        a = expression[1] # a
        b = expression[2] # b

        if b[0] == "num" and b[1] == 0:
            self.code.append("SUB 0")
        elif a[0] == "num" and a[1] == 0:
            self.code.append("SUB 0")
        elif a[0] == "num" and b[0] == "num":
            result = a[1] // b[1]
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
            self.code.append("SUB 0")
            self.code.append("STORE 3")
            self.code.append("STORE 4")

            # wynik (na razie ma być 0)
            self.code.append("STORE 5")

            # k
            self.code.append("SET 1")
            self.code.append("STORE 6")
            self.code.append("STORE 9")

            # ładujemy dzielną
            self.generate_code_expression(a)

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
            self.code.append("SUB 0")
            self.code.append("SUB 1")
            self.code.append("STORE 1")

            # zapisujemy pomocnicze |a|
            self.code.append("STORE 7")
            
            # ładujemy dzielnik
            self.generate_code_expression(b)

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
            self.code.append("SUB 0")
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
            self.code.append("JZERO 10")

            self.code.append("LOAD 2")
            self.code.append("SUB 7")
            self.code.append("STORE 7")

            self.code.append("LOAD 5")
            self.code.append("ADD 9")
            self.code.append("STORE 5")
            self.code.append("SUB 0")
            self.code.append("SUB 5")
            self.code.append("STORE 5")

            self.code.append("LOAD 4")
            self.code.append("JZERO 4")
            self.code.append("SUB 0")
            self.code.append("SUB 7")
            self.code.append("STORE 7")
            self.code.append("LOAD 5")

    def modulo(self, expression):
        self.divide(expression)
        self.code.append("LOAD 7")

    def handle_array_at_index(self, name, index):
        address = 0
        # w 1 przechowujemy adres komórki tablicy jesli nie odwołujemy sie do niej przez liczbe
        first_index = self.symbol_table[name].first_index
        memory_offset_of_first_index = self.symbol_table.get_address([name, first_index])
        array_offset = memory_offset_of_first_index - first_index

        if isinstance(index, int):
            address = self.symbol_table.get_address([name, index])
        elif isinstance(index, tuple) and index[0] == "id":
            if isinstance(index[1], tuple) and index[1][0] == "undeclared":
                if index[1][1] in self.symbol_table.iterators:
                    iterator_address = self.symbol_table.get_iterator(index[1][1])
                    self.code.append(f"SET {array_offset}")
                    self.code.append(f"ADD {iterator_address}")
                    self.code.append(f"STORE 1")
                    #sprawdzanie czy jest w zakresie
                else:
                    raise Exception(f"Undeclared index variable '{index[1][1]}'.")
            elif isinstance(index[1], str):
                name = index[1]
                variable_address = self.symbol_table.get_address(name)
                if not self.symbol_table[name].initialized:
                    raise Exception(f"Error: Uninitialized variable '{name}'")
                self.code.append(f"SET {array_offset}")
                self.code.append(f"ADD {variable_address}")
                self.code.append("STORE 1")
                # moze dodac sprawdzanie czy jest w zakresie
            else:
                raise Exception(f"Error: Invalid index type '{index}'")
        else:
            raise Exception(f"Error: Invalid index type '{index}'")
        return address

    def simplify_condition_if_possible(self, condition):
        condition_type = condition[0]
        left = condition[1]
        right = condition[2]

        if left[0] == "num" and right[0] == "num":
            left_value = left[1]
            right_value = right[1]
            if condition_type == "equal":
                return left_value == right_value
            elif condition_type == "notequal":
                return left_value != right_value
            elif condition_type == "greater":
                return left_value > right_value
            elif condition_type == "less":
                return left_value < right_value
            elif condition_type == "greaterequal":
                return left_value >= right_value
            elif condition_type == "lessequal":
                return left_value <= right_value
            else:
                raise Exception(f"Error: Invalid condition type '{condition_type}'")
        elif left == right:
            if condition_type in ["equal", "greaterequal", "lessequal"]:
                return True
            else:
                return False
        else:
            return condition
        
    def generate_condition_jumps(self, condition):
        # a _operator_ b <=> a - b _operator_ 0
        operator = condition[0]
        left = condition[1]
        right = condition[2]

        self.generate_code_expression(right)
        self.code.append("STORE 10")
        self.generate_code_expression(left)
        self.code.append("SUB 10")

        if operator == "equal":
            self.code.append("JZERO 2")
            self.code.append("JUMP end")
        elif operator == "notequal":
            self.code.append("JZERO 2")
            self.code.append("JUMP 2")
            self.code.append("JUMP end")
        elif operator == "greater":
            self.code.append("JPOS 2")
            self.code.append("JUMP end")
        elif operator == "less":
            self.code.append("JNEG 2")
            self.code.append("JUMP end")
        elif operator == "greaterequal":
            self.code.append("JPOS 3")
            self.code.append("JZERO 2")
            self.code.append("JUMP end")
        elif operator == "lessequal":
            self.code.append("JNEG 3")
            self.code.append("JZERO 2")
            self.code.append("JUMP end")
        else:
            raise Exception(f"Error: Invalid condition type '{operator}'")


        