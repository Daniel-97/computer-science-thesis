import ijson
import sys

def main():

    if len(sys.argv) <= 1:
        print("Usage: python3 parser.py <json file>")
        sys.exit(-1)

    parser = ijson.parse(open(sys.argv[1], "rb"))
    for prefix, event, item in parser:
        print(prefix, event, item, '\n')
    
if __name__ == "__main__":
    main()