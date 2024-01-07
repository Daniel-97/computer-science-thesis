import ijson
import json
import sys
from argparse import ArgumentParser

MAX_FILE_SIZE_MB = 50000000 # 50 MB

def main():

    # Simple argument parser
    parser = ArgumentParser(description="json splitter CLI")
    parser.add_argument('-i', '--input', required=True)
    parser.add_argument('-o', '--output', required=True)
    args = parser.parse_args()

    # Open the json file
    with open(args.input, "rb") as file:

        array_item = ijson.items(file, "item")
        file_number = 0 # File number
        file_size = 0 # Size in bytes
        partial_file_content = ''
        partial_file = None

        # Loop through the array
        for item in array_item:

            for transaction in item.get("transactions", []):
                
                transaction = clean_transaction(transaction=transaction)
                #transaction = convert_transaction_field(transaction=transaction)

                transaction_json = ('' if file_size == 0 else ',\n') + json.dumps(transaction)

                partial_file_content += transaction_json
                file_size += len(transaction_json)
                
                if file_size > MAX_FILE_SIZE_MB:
                    save_file(path=f'{args.output}/transactions-{file_number}.json',content=partial_file_content)
                    file_number += 1
                    file_size = 0
                    partial_file_content = ''

            # Need for last file saving
            if partial_file is not None:
                save_file(path=f'{args.output}/transactions-{file_number}.json',content=partial_file_content)
                break

def save_file(path, content):
    f = open(path, 'w')
    f.write('[\n' + content + '\n]')
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