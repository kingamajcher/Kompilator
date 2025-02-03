from symbol_table import *

class CodeGenerator:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.code = []
        self.iterators = []
        self.symbol_table.current_procedure = None
        self.previous_procedure = None
        self.defined_procedures = set()


    def generate(self, ast):
        if ast[0] == 'program':
            _, procedures, main = ast
            procedures_start = len(self.code)
            self.code.append("JUMP main")
            self.generate_code_procedures(procedures)
            main_start = len(self.code)
            self.code[procedures_start] = f"JUMP {main_start}"
            self.generate_code_main(main)
            self.code.append("HALT")
        return "\n".join(self.code)


    def generate_code_procedures(self, procedures):
        for procedure in procedures:
            if procedure[0] == "procedure":
                self.generate_code_procedure(procedure)


    def generate_code_procedure(self, procedure):
        _, proc_head, declarations, commands = procedure
        name, parameters = proc_head

        """if name in self.defined_procedures:
            raise Exception(f"Error: Redefinition of procedure '{name}'")
        self.defined_procedures.add(name)

        for parameter in parameters:
            self.symbol_table.is_parameter_valid(parameter, name)"""
                
        self.symbol_table.add_procedure(name, parameters, declarations, commands)

        self.symbol_table.current_procedure = name
        procedure_start = len(self.code)

        if self.symbol_table.procedures[name].memory_offset is None:
            self.symbol_table.procedures[name].memory_offset = procedure_start

        self.generate_code_commands(commands)
        procedure = self.symbol_table.procedures[name]

        # call count sprawdic
        return_memory_index = procedure.return_registers[procedure.call_count]

        self.code.append(f"RTRN {return_memory_index}")

        self.symbol_table.current_procedure = None
      

    def generate_code_main(self, main):
        _, declarations, commands = main
        self.generate_code_commands(commands)


    def generate_code_commands(self, commands):
        for command in commands:
            self.generate_code_command(command)


    def generate_code_command(self, command):
        command_type = command[0]
        if command_type == "assign":
            _, identifier, expression = command
            self.generate_code_assign(identifier, expression)
        elif command_type == "if_else":
            _, condition, true_commands, false_commands = command
            self.generate_code_if_else(condition, true_commands, false_commands)
        elif command_type == "if":
            _, condition, true_commands = command
            self.generate_code_if(condition, true_commands)
        elif command_type == 'while':
            _, condition, commands = command
            self.generate_code_while(condition, commands)
        elif command_type == "repeat":
            _, commands, condition = command
            self.generate_code_repeat(commands, condition)
        elif command_type == "for_to":
            _, iterator, start_value, end_value, commands = command
            self.generate_code_for(iterator, start_value, end_value, commands, False)
        elif command_type == "for_downto":
            _, iterator, start_value, end_value, commands = command
            self.generate_code_for(iterator, start_value, end_value, commands, True)
        elif command_type == "read":
            _, identifier = command
            self.generate_code_read(identifier)
        elif command_type == "write":
            _, value = command
            self.generate_code_write(value)
        elif command_type == "proc_call":
            _, name, arguments = command
            self.generate_code_proc_call(name, arguments)
                
    def generate_code_assign(self, variable, expression):
        if isinstance(variable, tuple):
            variable_type = variable[0]
            if variable_type == "array":
                name = variable[1]
                index = variable[2]
                self.handle_array_at_index(name, index)
                self.code.append("LOAD 12")
                self.code.append("STORE 13")
                self.generate_code_expression(expression)
                self.code.append("STOREI 13")
            elif variable_type == "other":
                if variable[1] in self.symbol_table.iterators:
                    raise Exception(f"Error: Cannot assign value to iterator '{variable[1]}'")
                else:
                    address = self.symbol_table.get_address_in_procedure(variable[1])
                    self.generate_code_expression(expression)
                    if isinstance(address, Variable):
                        self.code.append(f"STOREI {address}")
                    else:
                        self.code.append(f"STORE {address}")

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
                if start_value[1] < end_value[1]:
                    raise Exception("Error: Invalid range for loop")
            else:
                if start_value[1] > end_value[1]:
                    raise Exception("Error: Invalid range for loop")
                
        if iterator in self.symbol_table:
            raise Exception(f"Error: Redeclaration of iterator '{iterator}'")
        
        self.code.append("SET 1")
        self.code.append("STORE 10")
        
        if downto:
            operation = "SUB 10"
        else:
            operation = "ADD 10"

        self.iterators.append(iterator)
        start_address, end_address = self.symbol_table.add_iterator(iterator)

        self.generate_code_expression(end_value)
        self.code.append(operation)
        self.code.append(f"STORE {end_address}")
        self.generate_code_expression(start_value)
        self.code.append(f"STORE {start_address}")

        for_start = len(self.code)

        self.code.append(f"SUB {end_address}")

        end_invalid_range = len(self.code)
        if downto:
            self.code.append("JNEG end_invalid_range")
        else:
            self.code.append("JPOS end_invalid_range")

        commands_start = len(self.code)
        self.code.append("JZERO end_of_for")
        self.generate_code_commands(commands)
        self.code.append(f"LOAD {start_address}")
        self.code.append(f"{operation}")
        self.code.append(f"STORE {start_address}")

        for_end = len(self.code)
        self.code[commands_start] = f"JZERO {for_end - for_start - 1}"
        jump = str(-(for_end - for_start + 1))
        self.code.append(f"JUMP {jump}")
        end = len(self.code)
        self.code[end_invalid_range] = self.code[end_invalid_range].replace("end_invalid_range", str(end - end_invalid_range))


    def generate_code_read(self, identifier):
        if isinstance(identifier, tuple):
            identifier_type = identifier[0]
            if identifier_type == "array":
                name = identifier[1]
                index = identifier[2]
                self.handle_array_at_index(name, index)
                self.code.append("GET 0")
                self.code.append("STOREI 12")
            elif identifier_type == "other":
                if identifier[1] in self.symbol_table.iterators:
                    iterator = self.symbol_table.get_iterator(identifier[1])
                    iterator_address = iterator.memory_offset
                    self.code.append(f"GET {iterator_address}")
                else:
                    address = self.symbol_table.get_address_in_procedure(identifier[1][1])
                    if isinstance(address, Variable):
                        self.code.append("GET 0")
                        self.code.append(f"STOREI {address}")
                    else:
                        raise Exception(f"Error: Undeclared variable '{identifier[1][1]}'")
        else:
            if identifier in self.symbol_table:
                self.symbol_table[identifier].initialized = True
                address = self.symbol_table.get_address(identifier)
                self.code.append(f"GET {address}")
            elif identifier in self.symbol_table.iterators:
                raise Exception(f"Error: Cannot read to iterator '{identifier}'")

    def generate_code_write(self, value):
        write_type = value[0]
        if write_type == "id":
            if isinstance(value[1], tuple):
                value_type = value[1][0]
                if value_type == "array":
                    name = value[1][1]
                    index = value[1][2]
                    self.handle_array_at_index(name, index)
                    self.code.append("LOADI 12")
                    self.code.append("PUT 0")
                elif value_type == "other":
                    if value[1][1] in self.symbol_table.iterators:
                        iterator = self.symbol_table.get_iterator(value[1][1])
                        iterator_address = iterator.memory_offset
                        self.code.append(f"PUT {iterator_address}")
                    else:
                        address = self.symbol_table.get_address_in_procedure(value[1][1])
                        if isinstance(address, Variable):
                            self.code.append(f"LOADI {address}")
                            self.code.append("PUT 0")
                        else:
                            raise Exception(f"Error: Undeclared variable '{value[1][1]}'")
                else:
                    raise Exception(f"Error: Invalid value type '{value_type}' for WRITE")
            else:
                variable = self.symbol_table.get_address(value[1])
                self.code.append(f"PUT {variable}")
        elif write_type == "num":
            self.code.append(f"SET {value[1]}")
            self.code.append(f"PUT 0")
        else:
            raise Exception(f"Error: invalid value type '{value[0]}' for WRITE")

    def generate_code_proc_call(self, name, arguments):
        if name not in self.symbol_table.procedures:
            raise Exception(f"Error: Unknown procedure '{name}'.")

        if name == self.symbol_table.current_procedure:
            raise Exception(f"Error: Recursive call of procedure '{name}'.")
        
        self.previous_procedure = self.symbol_table.current_procedure
        self.symbol_table.current_procedure = name
            
        for argument in arguments:
            if argument not in self.symbol_table:
                raise Exception(f"Error: Undeclared argument '{argument}' for procedure '{name}'.")
            
        procedure = self.symbol_table.get_procedure(self.symbol_table.current_procedure)
        parameters = procedure.parameters
        
        if len(arguments) != len(parameters):
            raise Exception(f"Error: Incorrect number of arguments for procedure {name}. Expected {len(parameters)}, got {len(arguments)}.")
        
        for i, (parameter_name, parameter_type) in enumerate(parameters.items()):
            argument = arguments[i]

            if isinstance(parameter_type, Array):
                if argument not in self.symbol_table or not isinstance(self.symbol_table[argument], Array):
                    raise Exception(f"Expected array for parameter '{parameter_name}', but got variable '{argument}'.")
            elif argument in self.symbol_table and isinstance(self.symbol_table[argument], Array):
                raise Exception(f"Expected variable for parameter '{parameter_name}', but got array '{argument}'.")


        for parameter, argument in zip(parameters, arguments):
            parameter_address = parameters[parameter]
            argument_address = self.symbol_table.get_address(argument)
            self.code.append(f"SET {argument_address}")
            self.code.append(f"STORE {parameter_address}")
        
        procedure = self.symbol_table.procedures[name]

        return_memory_index = procedure.return_registers[procedure.call_count]
        procedure.call_count += 1
        
        current_code_len = len(self.code)
        self.code.append(f"SET {current_code_len + 3}")
        self.code.append(f"STORE {return_memory_index}")
        procedure_offset = procedure.memory_offset
        current_code_len = len(self.code)
        self.code.append(f"JUMP {procedure_offset - current_code_len}")

        procedure.call_count -= 1

        if self.previous_procedure:
            self.symbol_table.current_procedure = self.previous_procedure
        else:
            self.symbol_table.current_procedure = None

                
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
    
    def add(self, expression):
        a = expression[1]
        b = expression[2]

        if a[0] == "num" and b[0] == "num":
            result = a[1] + b[1]
            self.code.append(f"SET {result}")
        else:
            self.generate_code_expression(expression[1])
            self.code.append("STORE 1")
            self.generate_code_expression(expression[2])
            self.code.append("ADD 1")

    def substract(self, expression):
        a = expression[1]
        b = expression[2]

        if a[0] == "num" and b[0] == "num":
            result = a[1] - b[1]
            self.code.append(f"SET {result}")
        else:
            self.generate_code_expression(expression[2])
            self.code.append("STORE 1")
            self.generate_code_expression(expression[1])
            self.code.append("SUB 1")

    def multiply(self, expression):
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
            # p5 -> result
            # p6 -> helper b for checking if number is odd

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
        a = expression[1]
        b = expression[2]

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
            #self.code.append("STORE 9")

            # ładujemy dzielną
            self.generate_code_expression(a)

            # jesli jest zerem to dziki skok na koniec zeby zwracalo od razu zero
            self.code.append("JZERO 78")

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
            self.code.append("JZERO 67")

            # jesli jest 1 to dziki jump i zwraca dzielną
            """self.code.append("STORE 2")
            
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
            self.code.append("JUMP 68")

            # jesli niedodatnie to wykona, jeśli dodatnie to skoczy o 6
            self.code.append("LOAD 2")"""
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

    def handle_identifier(self, expression):
        if isinstance(expression, tuple):
            if expression[0] == "array":
                name = expression[1]
                index = expression[2]
                self.handle_array_at_index(name, index)
                self.code.append("LOADI 12")
            elif expression[0] == "other":
                if expression[1] in self.symbol_table.iterators:
                    iterator = self.symbol_table.get_iterator(expression[1])
                    iterator_address = iterator.memory_offset
                    self.code.append(f"LOAD {iterator_address}")
                elif isinstance(self.symbol_table.get_address_in_procedure(expression[1]), Variable):
                    address = self.symbol_table.get_address_in_procedure(expression[1])
                    self.code.append(f"LOADI {address}")
                else:
                    raise Exception(f"Error: undeclared variable '{expression[1]}'")
        elif isinstance(expression[0], str):
            name = expression
            if name in self.symbol_table:
                address = self.symbol_table.get_address(name)
                self.code.append(f"LOAD {address}")
            else:
                raise Exception(f"Error: unknown variable '{name}'")
        else:
            raise Exception("Error: wrong expression id format")

    def handle_array_at_index(self, name, index):
        if name not in self.symbol_table:
            raise Exception(f"Error: Array '{name}' not declared")
        if not isinstance(self.symbol_table[name], Array):
            raise Exception(f"Error: '{name}' is not an array")
        first_index = self.symbol_table[name].first_index
        memory_offset_of_first_index = self.symbol_table.get_address([name, first_index])
        array_offset = memory_offset_of_first_index - first_index # miejsce, gdzie w tablicy było by zero

        if isinstance(index, int): # odwołanie do konkretnej liczby
            address = self.symbol_table.get_address([name, index])
            self.code.append(f"SET {address}")
            self.code.append(f"STORE 12")
        elif isinstance(index, tuple) and index[0] == "id": # odwołanie do identifiera
            if isinstance(index[1], tuple) and index[1][0] == "other":
                name = index[1][1]
                if name in self.symbol_table.iterators:
                    #iterator_address, _ = self.symbol_table.get_iterator(name)
                    iterator = self.symbol_table.get_iterator(name)
                    iterator_address = iterator.memory_offset
                    self.code.append(f"SET {array_offset}")
                    self.code.append(f"ADD {iterator_address}")
                    self.code.append(f"STORE 12")
                elif name in self.symbol_table.current_procedure:
                    if name in self.symbol_table.procedures[self.symbol_table.current_procedure].local_variables:
                        variable_address = self.symbol_table.procedures[self.symbol_table.current_procedure].local_variables[name]
                        self.code.append(f"SET {array_offset}")
                        self.code.append(f"ADD {variable_address}")
                        self.code.append(f"STORE 12")
                    else:
                        raise Exception(f"Undeclared index variable '{name}'.")
                elif name in self.symbol_table:
                    variable_address = self.symbol_table.get_address(name)
                    self.code.append(f"SET {array_offset}")
                    self.code.append(f"ADD {variable_address}")
                    self.code.append(f"STORE 12")
                else:
                    raise Exception(f"Undeclared index variable '{name}'.")
            elif isinstance(index[1], str): # odwołanie do zmiennej
                name = index[1]
                variable_address = self.symbol_table.get_address(name)
                if not self.symbol_table[name].initialized:
                    raise Exception(f"Error: Uninitialized variable '{name}'")
                self.code.append(f"SET {array_offset}")
                self.code.append(f"ADD {variable_address}")
                self.code.append("STORE 12")
            else:
                raise Exception(f"Error: Invalid index type '{index}'")
        else:
            raise Exception(f"Error: Invalid index type '{index}'")