import ijson
import json
import sys
from argparse import ArgumentParser

MAX_FILE_SIZE = 50000000 # 50 MB

def main():

    # Simple argument parser
    parser = ArgumentParser(description="json splitter CLI")
    parser.add_argument('-i', '--input', required=True, help="Input file")
    parser.add_argument('-o', '--output', required=True, help="Output folder")
    parser.add_argument('-f', '--format', required=True, help="Output format", choices=["json", "csv"])
    args = parser.parse_args()

    # Open the json file
    with open(args.input, "rb") as file:

        array_item = ijson.items(file, "item")
        file_number = 0 # File number
        file_content = ''

        # Loop through the array
        for item in array_item:

            for transaction in item.get("transactions", []):
                
                transaction = clean_transaction(transaction=transaction)
                #transaction = convert_transaction_field(transaction=transaction)
                file_content += generate_file_row(data=transaction, format=args.format, is_first_row=len(file_content) == 0)

                if sys.getsizeof(file_content) > MAX_FILE_SIZE:
                    print("Saving file...")
                    save_file(path=f'{args.output}/transactions-{file_number}.json',content=file_content, format=args.format)
                    file_number += 1
                    file_content = ''

def generate_file_row(data, format, is_first_row):
    if format == 'json':
        return (',\n' if not is_first_row else '') + json.dumps(data)
    elif format == 'csv':
        return ''


def save_file(path, content, format):
    with open(path, 'w') as f:
        if format == 'json':
            f.write(f"[\n{content}\n]")
        f.close()
        print(f'File {path} saved! Size: {len(content)} byte')

def clean_transaction(transaction):

    # if int(transaction['logsBloom'], 16) == 0:
    #                 del transaction['logsBloom']

    del transaction['logsBloom'] 
    del transaction['blockHash']
    del transaction['v']
    del transaction['r']
    del transaction['s']
    del transaction['transactionIndex']
    del transaction['root']
    del transaction['chainId']

    return transaction

def convert_transaction_field(transaction):
    transaction['gas'] = int(transaction['gas'], 16)
    transaction['gasPrice'] = int(transaction['gasPrice'], 16)

    return transaction

if __name__ == "__main__":
    main()