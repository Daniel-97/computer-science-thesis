import ijson
import argparse
from eth._utils import address
from eth_utils import to_canonical_address
from trie_hex import Trie, NodeType
from model_parser.complex_model_parser import ComplexModelParser
from model_parser.simple_model_parser import SimpleModelParser
from ethereum_client import EthereumClient
import gzip
from dotenv import load_dotenv

class EthereumJsonParser:

    def __init__(
            self,
            output_folder: str,
            input_file_path: str,
            max_file_size_mb: int,
            file_format: str,
            trie_path: str
        ):

        # PARAMETERS
        self.file_format = file_format

        # ETH CLIENT
        self.eth_client = EthereumClient()

        # TRIE
        self.trie = Trie()
        self.trie.load_trie(trie_path)

        # MODELS PARSER
        input_file_name = input_file_path.split('/')[-1].split('.')[0]
        self.model1_parser = ComplexModelParser(input_file_name, output_folder, max_file_size_mb, file_format)
        self.model2_parser = SimpleModelParser(input_file_name, output_folder, max_file_size_mb, file_format)

        # STATS
        self.parsed_transaction = 0
    
    def close(self):
        print(f"Tot. parsed transaction: {self.parsed_transaction}")
        self.model1_parser.parse_trie(self.trie)
        self.model2_parser.parse_trie(self.trie)
        self.model1_parser.close_parser()
        self.model2_parser.close_parser()
        print(f"eth_client tot_requests: {self.eth_client.tot_requests}, avg_time(s): {self.eth_client.avg_response_time}")
        print(f'Trie nodes: {len(self.trie.datrie)}')
        print(f'Trie lookup time: {self.trie.lookup_time}')


    def clean_transaction(self, transaction: dict):
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

    def clean_block(self, block: dict):
        del block['logsBloom']
        del block['@type']
        if "ommers" in block:
            del block["ommers"]
        if "miner" in block:
            block["minerAddress"] = block.get("miner").get("address")
            del block["miner"]
        
    def convert_block_field(self, block: dict) -> dict:
        self.convert_filed(block, 'number')
        self.convert_filed(block, 'gasLimit')
        self.convert_filed(block, 'gasUsed')
        self.convert_filed(block, 'timestamp')

    def convert_transaction_field(self, transaction: dict) -> dict:
        self.convert_filed(transaction, 'gas')
        self.convert_filed(transaction, 'gasPrice')
        self.convert_filed(transaction, 'gasUsed')
        self.convert_filed(transaction, 'value')

    def convert_filed(self, dict: dict, field_name: str) -> int:
        if field_name in dict:
            dict[field_name] = int(dict[field_name],16)
    
    def parse_file(self, file_path: str, start_block: int, end_block: int):

        file_name = file_path.split('/')[-1]
        print(f'Start parsing file {file_name} from block {start_block} to block {end_block}')
        with gzip.open(file_path, "rb") as file:

            close = False
            parse_block = False
            start_block_hex = hex(start_block)
            end_block_hex = hex(end_block)

            # Loop through the array
            for block in ijson.items(file, "item"):
                
                if close:
                    break
                
                # Start parsing data from the start_block number
                if not parse_block and ( block['number'] == start_block_hex or int(block['number'],16) > start_block):
                    parse_block = True

                # Parse until end_block is reached
                if end_block_hex is not None and block['number'] == end_block_hex:
                    close = True

                if not parse_block or 'transactions' not in block:
                    continue

                transactions = block['transactions']
                del block['transactions']
                
                self.clean_block(block)
                self.convert_block_field(block)
                self.model1_parser.parse_block(block)

                for transaction in transactions:
                    self.parsed_transaction += 1
                    self.clean_transaction(transaction)
                    self.convert_transaction_field(transaction)

                    from_address = transaction.get('fromAddress')
                    to_address = transaction.get('toAddress')

                    # If the destination address is None then it is a smart contract creation
                    if to_address is None:
                        del transaction['input'] # Contains the smart contract code
                        # Generate the smart contract address
                        contract_address = address.generate_contract_address(
                            address=to_canonical_address(transaction.get("fromAddress")),
                            nonce=int(transaction.get("nonce"), 16)
                        )
                        transaction['contractAddress'] = "0x" + contract_address.hex()
                        self.model1_parser.parse_contract_creation(transaction)
                        self.model2_parser.parse_contract_creation(transaction, block)

                    # If there are logs in the transaction, or is in the trie of SC is an SC
                    elif 'logs' in transaction or self.trie.find(to_address[2:], NodeType.SC):
                        self.model1_parser.parse_contract_transaction(transaction)
                        self.model2_parser.parse_contract_transaction(transaction, block)

                    elif self.trie.find(to_address[2:], NodeType.EOA):
                        self.model1_parser.parse_eoa_transaction(transaction)
                        self.model2_parser.parse_eoa_transaction(transaction, block)

                    else:
                        #print(f"Unknown destination address {to_address} for transaction {transaction['hash']}")
                        self.model1_parser.parse_unknown_transaction(transaction)
                        self.model2_parser.parse_unknown_transaction(transaction, block)

if __name__ == "__main__":

    load_dotenv()
    # Simple argument parser
    parser = argparse.ArgumentParser(description="json splitter CLI")
    parser.add_argument('-i', '--input', required=True, help="Input file", type=str)
    parser.add_argument('-o', '--output', required=True, help="Output folder", type=str)
    parser.add_argument('-s', '--size', required=True, help="Max file size in mega bytes. -1 for no size limit", type=int)
    parser.add_argument('-f', '--format', required=True, help="File output format", choices=['json', 'csv'])
    parser.add_argument('-sb','--start-block', required=True, help="Start block number (integer)", type=int) # Start parsing from the specified block (included)
    parser.add_argument('-eb', '--end-block', required=True, help="End block number (integer)", type=int) # End parsing to this block number (included)
    parser.add_argument('-t', '--trie', required=True, help="Trie dump path", type=str)
    args = parser.parse_args()

    # Init ethereum json parser
    ethereum_parser = EthereumJsonParser(
        output_folder=args.output,
        input_file_path=args.input,
        max_file_size_mb=args.size,
        file_format=args.format,
        trie_path=args.trie
    )

    # Start parsing
    ethereum_parser.parse_file(
        file_path=args.input,
        start_block=args.start_block,
        end_block=args.end_block
    )

    ethereum_parser.close()