import ijson
import json
import sys

MAX_FILE_SIZE_MB = 50000000 # 50 MB

def main():

    if len(sys.argv) <= 1:
        print("Usage: python3 parser.py <json file>")
        sys.exit(-1)

    # Open the json file
    with open(sys.argv[1], "rb") as file:

        array_item = ijson.items(file, "item")
        file_number = 0 # File number
        file_size = 0 # Size in bytes
        partial_file = None

        # Loop through the array
        for item in array_item:
            
            #Skip block with no transaction
            if 'transactions' not in item:
                continue

            for transaction in item["transactions"]:

                if partial_file is None:
                    partial_file = open(f'transactions/transactions-{file_number}.json', 'w')
                    file_number += 1
                    file_size = 0
                    partial_file_content = ''
                    partial_file.write('[\n')
                    print(f'Processing file {file_number}...')
                
                transaction = clean_transaction(transaction=transaction)
                #transaction = convert_transaction_field(transaction=transaction)

                transaction_json = ('' if file_size == 0 else ',\n') + json.dumps(transaction)

                partial_file_content += transaction_json
                file_size += len(transaction_json)
                
                if file_size > MAX_FILE_SIZE_MB:
                    partial_file.write(partial_file_content + '\n]')
                    partial_file.close()
                    partial_file = None
                    print(f'File {file_number} saved! Size: {file_size} byte')

            # Need for last file saving
            if partial_file is not None and file_number == 5:
                partial_file.write(partial_file_content + '\n]')
                partial_file.close()
                partial_file = None
                break

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