import ijson
from argparse import ArgumentParser
from eth._utils import address
from eth_utils import to_canonical_address
from trie_hex import Trie
from model_parser.complex_model_parser import ComplexModelParser
from model_parser.simple_model_parser import SimpleModelParser
from ethereum_client import EthereumClient
import gzip

def main():

    # ARGS PARSER
    args = init_arg_parser()

    # ETH CLIENT
    eth_client = EthereumClient()
    
    # TRIE
    SC_trie = Trie("SC") # Trie for contract address
    EOA_trie = Trie("EOA") # Trie for EAO address

    # MODELS PARSER
    model1_parser = ComplexModelParser(args)
    model2_parser = SimpleModelParser(args)

    # Open the json file
    with gzip.open(args.input, "rb") as file:

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
                    SC_trie.add(to_address[2:]) # Add the destination address to the trie
                    model1_parser.parse_contract_transaction(transaction)
                    model2_parser.parse_contract_transaction(transaction, block)

                elif EOA_trie.find(to_address[2:]):
                    model1_parser.parse_eoa_transaction(transaction)
                    model2_parser.parse_eoa_transaction(transaction, block)

                #Unknown destination address, need to use eth client
                else:
                    print(f"Unknown destination address {to_address} for transaction {transaction['hash']}")
                    if eth_client.is_contract(to_address):
                        SC_trie.add(to_address[2:])
                        model1_parser.parse_contract_transaction(transaction)
                        model2_parser.parse_contract_transaction(transaction, block)
                    else:
                        EOA_trie.add(to_address[2:])
                        model1_parser.parse_eoa_transaction(transaction)
                        model2_parser.parse_eoa_transaction(transaction, block)

    # Close operation
    SC_trie.save_trie()
    EOA_trie.save_trie()
    model1_parser.close_parser()
    model2_parser.close_parser()
    print(f"eth_client tot_requests: {eth_client.tot_requests}, avg_time: {eth_client.avg_response_time} sec")

    
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

def init_arg_parser():
    # Simple argument parser
    parser = ArgumentParser(description="json splitter CLI")
    parser.add_argument('-i', '--input', required=True, help="Input file")
    parser.add_argument('-o', '--output', required=True, help="Output folder")
    parser.add_argument('-s', '--size', required=True, help="Max file size in mega bytes. -1 for no size limit", type=int)
    parser.add_argument('-f', '--format', required=True, help="File output format", choices=['json', 'csv'])
    parser.add_argument('-t','--transaction', required=False, help="Number of transaction to save", type=int)

    return parser.parse_args()

if __name__ == "__main__":
    main()