import ijson
import json
from argparse import ArgumentParser
from eth._utils import address
from eth_utils import to_canonical_address
import time
from trie_hex import Trie

from file_splitter_helper import FileSplitterHelper

def main():

    # Simple argument parser
    parser = ArgumentParser(description="json splitter CLI")
    parser.add_argument('-i', '--input', required=True, help="Input file")
    parser.add_argument('-o', '--output', required=True, help="Output folder")
    parser.add_argument('-s', '--size', required=True, help="Max file size in mega bytes", type=int)
    parser.add_argument('-bn','--block', required=False, help="Number of block to save", type=int)
    args = parser.parse_args()

    # Splitter
    block_splitter = FileSplitterHelper('blocks', args.output, args.size)
    eoa_transaction_splitter = FileSplitterHelper('eoa-transactions', args.output, args.size)
    contract_transaction_splitter = FileSplitterHelper('contract-transactions', args.output, args.size)
    contract_creation_splitter = FileSplitterHelper('contract-creation', args.output, args.size)
    log_splitter = FileSplitterHelper('contract-logs', args.output, args.size)
    
    # Trie for contract address
    trie = Trie()

    trie_lookup = 0
    file_write = 0
    trie_add = 0

    # Open the json file
    with open(args.input, "rb") as file: #todo, add support for gzip file

        block_number = 0
        # Loop through the array
        for block in ijson.items(file, "item"):

            # Skip block with zero transaction
            if "transactions" not in block:
                continue

            # Save the first args.block, then exit
            if args.block is not None and block_number > args.block:
                break

            block_number += 1

            block_transactions = block.get("transactions", [])

            if 'transactions' in block:
                del block['transactions']

            tic = time.perf_counter()
            block_splitter.append(element=json.dumps(clean_block(block)))
            file_write += time.perf_counter() - tic

            for transaction_dict in block_transactions:
                
                transaction_dict = clean_transaction(transaction=transaction_dict)
                
                if transaction_dict.get('toAddress') is None:
                    # Generate the smart contract address
                    del transaction_dict['input']
                    contract_address = address.generate_contract_address(
                        address=to_canonical_address(transaction_dict.get("fromAddress")),
                        nonce=int(transaction_dict.get("nonce"), 16)
                    )
                    #Add the address to the trie       
                    trie.add(contract_address.hex())
                    transaction_dict['contractAddress'] = "0x" + contract_address.hex()
                    tic = time.perf_counter()
                    contract_creation_splitter.append(element=json.dumps(transaction_dict))
                    file_write += time.perf_counter() - tic

                else:
                    # Search the address in the trie (if present is is a smart contract invocation)
                    toAddress = transaction_dict.get('toAddress')

                    tic = time.perf_counter()
                    is_contract_address = trie.find(toAddress[2:])
                    toc = time.perf_counter()
                    trie_lookup += toc - tic

                    tic = time.perf_counter()

                    if is_contract_address:
                        
                        logs = transaction_dict.get('logs', [])
                        if 'logs' in transaction_dict:
                            del transaction_dict['logs']
                        contract_transaction_splitter.append(element=json.dumps(transaction_dict))
                        for log in logs:
                            log['transactionHash'] = transaction_dict['hash']
                            log_splitter.append(element=json.dumps(log))
                    else:
                        eoa_transaction_splitter.append(element=json.dumps(transaction_dict))

                    file_write += time.perf_counter() - tic

    # Safe close all splitter
    block_splitter.end_file()
    eoa_transaction_splitter.end_file()
    contract_transaction_splitter.end_file()
    contract_creation_splitter.end_file()
    log_splitter.end_file()

    print(f'total trie lookup: {trie_lookup}s')
    print(f'total file write: {file_write}s')
    print(f'total trie add: {trie_add}s')

    
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

if __name__ == "__main__":
    main()