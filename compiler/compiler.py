import sys
from lexer import MyLexer
from parser import MyParser

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 compiler.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    lexer = MyLexer()
    parser = MyParser()
    
    try:
        with open(input_file, "r") as file:
            source_code = file.read()
        
        tokens = lexer.tokenize(source_code)
        code = parser.parse(tokens)

        with open(output_file, "w") as f:
            f.write(code)
        
        print(f"\nCode saved to '{output_file}'.")
    
    except Exception as e:
        print(f"{e}")

if __name__ == "__main__":
    main()