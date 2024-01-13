import ijson
import csv
import json
import sys
import io
from argparse import ArgumentParser
import web3

from file_splitter_helper import FileSplitterHelper

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
        block_splitter = FileSplitterHelper('blocks', args.output + '/blocks', args.size)
        transaction_splitter = FileSplitterHelper('transactions', args.output + '/transactions', args.size)

        # Loop through the array
        for item in array_item:

            block_transactions = item.get("transactions", [])
            if 'transactions' in item:
                del item['transactions']
            block_splitter.append(element=json.dumps(clean_block(item)))

            for transaction_dict in block_transactions:
                
                transaction_dict['timestamp'] = item.get('timestamp')
                transaction_dict = clean_transaction(transaction=transaction_dict)
                
                file_content = generate_file_row(data=transaction_dict, format=args.format, is_first_row=False)
                transaction_splitter.append(element=file_content)

def generate_file_row(data: dict, format, is_first_row):
    
    if format == 'json':
        return json.dumps(data)
    
    elif format == 'csv':
        
        csv_buffer = io.StringIO()
        csv_writer = csv.DictWriter(csv_buffer, data.keys(), extrasaction='ignore')

        # Write the header csv
        if is_first_row:
            csv_writer.writeheader()

       # print(flat_data, type(flat_data), flat_data.keys())
        csv_writer.writerow(data)

        csv_string = csv_buffer.getvalue()
        csv_buffer.close()
        return  csv_string
    
def clean_transaction(transaction: dict) -> dict:

    del transaction['nonce']
    del transaction['transactionIndex']
    del transaction['chainId']
    del transaction['v']
    del transaction['r']
    del transaction['s']
    del transaction['logsBloom']
    del transaction['root']

    transaction['toType'] = transaction.get('to').get('@type')
    transaction['toAddress'] = transaction.get('to').get('address')
    transaction['fromType'] = transaction.get('from').get('@type')
    transaction['fromAddress'] = transaction.get('from').get('address')

    del transaction['to']
    del transaction['from']

    return transaction

def clean_block(block: dict) -> dict:
    del block['logsBloom']

    return block

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