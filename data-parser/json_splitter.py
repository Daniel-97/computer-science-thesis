import ijson
import json
from argparse import ArgumentParser
from eth._utils import address
from eth_utils import to_canonical_address
from trie import HexaryTrie
import time

from file_splitter_helper import FileSplitterHelper

def main():

    # Simple argument parser
    parser = ArgumentParser(description="json splitter CLI")
    parser.add_argument('-i', '--input', required=True, help="Input file")
    parser.add_argument('-o', '--output', required=True, help="Output folder")
    parser.add_argument('-f', '--format', required=True, help="Output format", choices=["json", "csv"])
    parser.add_argument('-s', '--size', required=True, help="Max file size in mega bytes", type=int)
    args = parser.parse_args()

    # Splitter
    block_splitter = FileSplitterHelper('blocks', args.output + '/blocks', args.size)
    eoa_transaction_splitter = FileSplitterHelper('eoa-transactions', args.output + '/eoa-transactions', args.size)
    contract_transaction_splitter = FileSplitterHelper('contract-transactions', args.output + '/contract-transactions', args.size)
    smart_contract_creation_splitter = FileSplitterHelper('contract-creation',args.output + '/contract-creation', args.size)
    
    # Trie for contract address
    trie = HexaryTrie(db={})

    # Open the json file
    with open(args.input, "rb") as file:

        array_item = ijson.items(file, "item")

        # Loop through the array
        for item in array_item:

            block_transactions = item.get("transactions", [])

            if 'transactions' in item:
                del item['transactions']
            block_splitter.append(element=json.dumps(clean_block(item)))

            for transaction_dict in block_transactions:
                
                transaction_dict = clean_transaction(transaction=transaction_dict)
                
                if transaction_dict.get('toAddress') is None:
                    # Generate the smart contract address
                    del transaction_dict['input']
                    contract_address = address.generate_contract_address(
                        address=to_canonical_address(transaction_dict.get("fromAddress")),
                        nonce=int(transaction_dict.get("nonce"), 16)
                    )
                    trie.set(contract_address, b'0') #Add the address to the trie (at least one byte is required)
                    transaction_dict['contractAddress'] = "0x" + contract_address.hex()
                    smart_contract_creation_splitter.append(element=json.dumps(transaction_dict))

                else:
                    # Search the address in the trie (if present is is a smart contract invocation)
                    toAddress = transaction_dict.get('toAddress')

                    #tic = time.perf_counter()
                    if trie.exists(bytes.fromhex(toAddress[2:])): # todo troppo oneroso in tempo, trovare altra soluzione
                        contract_transaction_splitter.append(element=json.dumps(transaction_dict))
                    else:
                        eoa_transaction_splitter.append(element=json.dumps(transaction_dict))
                    #toc = time.perf_counter()
                    #print(toc - tic)
    
def clean_transaction(transaction: dict) -> dict:

    del transaction['chainId']
    del transaction['logsBloom']
    del transaction['type']
    del transaction['@type']
    del transaction['v']
    del transaction['r']
    del transaction['s']

    transaction['toAddress'] = transaction.get('to').get('address')
    transaction['fromAddress'] = transaction.get('from').get('address')

    del transaction['to']
    del transaction['from']

    if "logs" in transaction:
        del transaction['logs']

    return transaction

def clean_block(block: dict) -> dict:
    del block['logsBloom']
    if "ommers" in block:
        del block["ommers"]
    if "miner" in block:
        block["minerType"] = block.get("miner").get("@type")
        block["minerAddress"] = block.get("miner").get("address")
        del block["miner"]
    

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