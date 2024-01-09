import ijson
import csv
import json
import sys
import io
from argparse import ArgumentParser
from transaction import Transaction

def main():

    # Simple argument parser
    parser = ArgumentParser(description="json splitter CLI")
    parser.add_argument('-i', '--input', required=True, help="Input file")
    parser.add_argument('-o', '--output', required=True, help="Output folder")
    parser.add_argument('-f', '--format', required=True, help="Output format", choices=["json", "csv"])
    parser.add_argument('-s', '--size', required=True, help="Max file size in mega bytes", type=int)
    args = parser.parse_args()

    # Open the json file
    with open(args.input, "rb") as file:

        array_item = ijson.items(file, "item")
        file_number = 0 # File number
        file_content = ''

        # Loop through the array
        for item in array_item:

            for transaction_dict in item.get("transactions", []):
                
                transaction = Transaction(transaction_dict)
                #transaction = convert_transaction_field(transaction=transaction)
                file_content += generate_file_row(data=transaction, format=args.format, is_first_row=len(file_content) == 0)

                if sys.getsizeof(file_content) > args.size * 1000000:
                    print("Saving file...")
                    save_file(path=f'{args.output}/transactions-{file_number}.{args.format}',content=file_content, format=args.format)
                    file_number += 1
                    file_content = ''

def generate_file_row(data: Transaction, format, is_first_row):
    
    if format == 'json':
        return (',\n' if not is_first_row else '') + json.dumps(data.__dict__)
    
    elif format == 'csv':
        
        csv_buffer = io.StringIO()
        csv_writer = csv.DictWriter(csv_buffer, data.__dict__.keys(), extrasaction='ignore')

        # Write the header csv
        if is_first_row:
            csv_writer.writeheader()

       # print(flat_data, type(flat_data), flat_data.keys())
        csv_writer.writerow(data.__dict__)

        csv_string = csv_buffer.getvalue()
        csv_buffer.close()
        return  csv_string


def save_file(path, content, format):
    with open(path, 'w') as f:
        if format == 'json':
            f.write(f"[\n{content}\n]")
        elif format == 'csv':
            f.write(content)
        f.close()
        print(f'File {path} saved! Size: {len(content)} byte')

if __name__ == "__main__":
    main()