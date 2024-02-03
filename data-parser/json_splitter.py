import ijson
from argparse import ArgumentParser
from eth._utils import address
from eth_utils import to_canonical_address
import time
from trie_hex import Trie
from complex_model_parser import ComplexModelParser
from simple_model_parser import SimpleModelParser

from file_splitter_helper import FileSplitterHelper

def main():

    # Simple argument parser
    parser = ArgumentParser(description="json splitter CLI")
    parser.add_argument('-i', '--input', required=True, help="Input file")
    parser.add_argument('-o', '--output', required=True, help="Output folder")
    parser.add_argument('-s', '--size', required=True, help="Max file size in mega bytes. -1 for no size limit", type=int)
    parser.add_argument('-f', '--format', required=True, help="File output format", choices=['json', 'csv'])
    parser.add_argument('-t','--transaction', required=False, help="Number of transaction to save", type=int)
    args = parser.parse_args()
    
    SC_trie = Trie() # Trie for contract address
    EOA_trie = Trie() # Trie for EAO address

    # Model parser
    model1_parser = ComplexModelParser(args)
    model2_parser = SimpleModelParser(args)

    trie_lookup = 0

    # Open the json file
    with open(args.input, "rb") as file: #todo, add support for gzip file

        transaction_count = 0
        close = False
        # Loop through the array
        for block in ijson.items(file, "item"):

            if close:
                break

            # Skip block with zero transaction
            if "transactions" not in block:
                continue

            transactions = block.get("transactions", [])
            del block['transactions']

            model1_parser.parse_block(block=clean_block(block))

            for transaction in transactions:

                # Save the firsts args.block blocks, then exit
                if args.transaction is not None and transaction_count >= args.transaction:
                    close = True
                    break
                
                transaction_count += 1
                transaction = clean_transaction(transaction=transaction)

                to_address = transaction.get('toAddress')
                from_address = transaction.get('fromAddress')
                EOA_trie.add(from_address[2:]) # Add the EOA address to the EOA trie

                # If the destination address is None then it is a smart contract creation
                if to_address is None:
                    del transaction['input'] # Contains the smart contract code
                    # Generate the smart contract address
                    contract_address = address.generate_contract_address(
                        address=to_canonical_address(transaction.get("fromAddress")),
                        nonce=int(transaction.get("nonce"), 16)
                    )
                    #Add the address to the trie       
                    SC_trie.add(contract_address.hex())
                    transaction['contractAddress'] = "0x" + contract_address.hex()

                    # call model parser
                    model1_parser.parse_contract_creation(transaction)
                    model2_parser.parse_contract_creation(transaction, block)

                # If there are logs in the transaction, or is in the trie of SC is an SC
                elif 'logs' in transaction or SC_trie.find(to_address[2:]):
                    SC_trie.add(to_address) # Add the destination address to the trie
                    model1_parser.parse_contract_transaction(transaction)
                    model2_parser.parse_contract_transaction(transaction, block)

                # Check if it is a EOA transaction
                elif EOA_trie.find(to_address[2:]):
                    model1_parser.parse_eoa_transaction(transaction)
                    model2_parser.parse_eoa_transaction(transaction, block)
                
                # Otherwise is unknown
                else:
                    model1_parser.parse_unknown_transaction(transaction)
                    model2_parser.parse_unknown_transaction(transaction, block)


                # else:
                #     # Search the address in the trie (if present is is a smart contract invocation)
                #     tic = time.perf_counter()
                #     is_contract_address = SM_trie.find(to_address[2:])
                #     trie_lookup += time.perf_counter() - tic
                    
                #     if is_contract_address: 
                #         model1_parser.parse_contract_transaction(transaction)
                #         model2_parser.parse_contract_transaction(transaction, block)
                #     else:
                #         # Here the transaction can still be a smart contract invocation (smart contract created by other smart contract)

                #         # If there are logs in the transaction it means it is a smart contract invocation
                #         if 'logs' in transaction:
                #             SM_trie.add(to_address) # Add the destination address to the trie
                #             model1_parser.parse_contract_transaction(transaction)
                #             model2_parser.parse_contract_transaction(transaction, block)
                            
                #         else:
                #             model1_parser.parse_eoa_transaction(transaction)
                #             model2_parser.parse_eoa_transaction(transaction, block)


    print(f'total trie lookup: {trie_lookup}s')
    model1_parser.close_parser()
    model2_parser.close_parser()

    
def clean_transaction(transaction: dict) -> dict:

    del transaction['chainId']
    del transaction['logsBloom']
    #del transaction['type']
    #del transaction['@type']
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