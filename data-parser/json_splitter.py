import ijson
from argparse import ArgumentParser
from eth._utils import address
from eth_utils import to_canonical_address
from trie_hex import Trie
from model_parser.complex_model_parser import ComplexModelParser
from model_parser.simple_model_parser import SimpleModelParser
from ethereum_client import EthereumClient
import gzip

class EthereumJsonParser:

    def __init__(
            self,
            output_folder: str,
            max_file_size_mb: int,
            file_format: str,
            only_heuristic: bool,
        ):

        # PARAMETERS
        self.file_format = file_format
        self.only_heuristic = only_heuristic

        # ETH CLIENT
        self.eth_client = EthereumClient()

        # TRIE
        self.SC_trie = Trie('SC')
        self.EOA_trie = Trie('EOA')

        # MODELS PARSER
        self.model1_parser = ComplexModelParser(output_folder, max_file_size_mb, file_format)
        self.model2_parser = SimpleModelParser(output_folder, max_file_size_mb, file_format)

        # STATS
        self.parsed_transaction = 0
    
    # def start_parse(self, start_block: str, end_block: str):
        
    #     # BLOCKS NUMBER
    #     start_block = '0x0' if start_block is None else start_block
    #     end_block = None if end_block is None else end_block

    #     # Parse all the input files
    #     files = []
    #     for file_name in os.listdir(self.input_folder):
    #         if 'dump' in file_name: 
    #             files.append(f'{self.input_folder}/{file_name}')
    #     files.sort()

    #     for file_path in files:
    #         print(f'Start parsing file {file_path}')
    #         parsed_transaction = self.parse_file(file_path, start_block, end_block)
    #         self.parsed_transaction += parsed_transaction
    #         print(f'Parsed {parsed_transaction} transaction')
    
    def close(self):
        print(f"Tot. parsed transaction: {self.parsed_transaction}")
        self.SC_trie.save_trie()
        self.EOA_trie.save_trie()
        self.model1_parser.close_parser()
        self.model2_parser.close_parser()
        print(f"eth_client tot_requests: {self.eth_client.tot_requests}, avg_time(s): {self.eth_client.avg_response_time}")
        print(f'Trie lookup time(sec): SC {self.SC_trie.lookup_time}, EOA: {self.EOA_trie.lookup_time}')

    def clean_transaction(self, transaction: dict) -> dict:

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

    def clean_block(self, block: dict) -> dict:
        del block['logsBloom']
        if "ommers" in block:
            del block["ommers"]
        if "miner" in block:
            block["minerType"] = block.get("miner").get("@type")
            block["minerAddress"] = block.get("miner").get("address")
            del block["miner"]
        
        return block

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
                if not parse_block and block['number'] == start_block_hex:
                    parse_block = True

                # Parse until end_block is reached
                if end_block_hex is not None and block['number'] == end_block_hex:
                    close = True

                # Skip block with zero transaction
                if "transactions" not in block:
                    continue

                transactions = block.get("transactions", [])
                del block['transactions']
                
                if parse_block:
                    self.model1_parser.parse_block(block=self.clean_block(block))

                for transaction in transactions:
                    self.parsed_transaction += 1
                    transaction = self.clean_transaction(transaction=transaction)

                    to_address = transaction.get('toAddress')
                    from_address = transaction.get('fromAddress')
                    self.EOA_trie.add(from_address[2:]) # Add the EOA address to the EOA trie

                    # If the destination address is None then it is a smart contract creation
                    if to_address is None:
                        del transaction['input'] # Contains the smart contract code
                        # Generate the smart contract address
                        contract_address = address.generate_contract_address(
                            address=to_canonical_address(transaction.get("fromAddress")),
                            nonce=int(transaction.get("nonce"), 16)
                        )
                        #Add the address to the trie       
                        self.SC_trie.add(contract_address.hex())
                        transaction['contractAddress'] = "0x" + contract_address.hex()

                        # call model parser
                        if parse_block:
                            self.model1_parser.parse_contract_creation(transaction)
                            self.model2_parser.parse_contract_creation(transaction, block)

                    # If there are logs in the transaction, or is in the trie of SC is an SC
                    elif 'logs' in transaction or self.SC_trie.find(to_address[2:]):
                        self.SC_trie.add(to_address[2:]) # Add the destination address to the trie
                        if parse_block:
                            self.model1_parser.parse_contract_transaction(transaction)
                            self.model2_parser.parse_contract_transaction(transaction, block)

                    elif self.EOA_trie.find(to_address[2:]):

                        if parse_block:
                            self.model1_parser.parse_eoa_transaction(transaction)
                            self.model2_parser.parse_eoa_transaction(transaction, block)

                    #Unknown destination address, need to use eth client
                    else:

                        #print(f"Unknown destination address {to_address} for transaction {transaction['hash']}")

                        # If only heuristic is true, do not use local eth client for node classification
                        if self.only_heuristic:
                            if parse_block:
                                self.model1_parser.parse_unknown_transaction(transaction)
                                self.model2_parser.parse_unknown_transaction(transaction, block)

                        else:

                            if self.eth_client.is_contract(to_address):
                                self.SC_trie.add(to_address[2:])
                                if parse_block:
                                    self.model1_parser.parse_contract_transaction(transaction)
                                    self.model2_parser.parse_contract_transaction(transaction, block)
                            else:
                                self.EOA_trie.add(to_address[2:])
                                if parse_block:
                                    self.model1_parser.parse_eoa_transaction(transaction)
                                    self.model2_parser.parse_eoa_transaction(transaction, block)

if __name__ == "__main__":
    # Simple argument parser
    parser = ArgumentParser(description="json splitter CLI")
    parser.add_argument('-i', '--input', required=True, help="Input file", type=str)
    parser.add_argument('-o', '--output', required=True, help="Output folder", type=str)
    parser.add_argument('-s', '--size', required=True, help="Max file size in mega bytes. -1 for no size limit", type=int)
    parser.add_argument('-f', '--format', required=True, help="File output format", choices=['json', 'csv'])
    parser.add_argument('-oh','--only-heuristic', required=True, help="Use only the heuristic classification (no local eth client)", type=bool)
    parser.add_argument('-sb','--start-block', required=True, help="Start block number (integer)", type=int) # Start parsing from the specified block (included)
    parser.add_argument('-eb', '--end-block', required=True, help="End block number (integer)", type=int) # End parsing to this block number (included)
    args = parser.parse_args()

    # Init ethereum json parser
    ethereum_parser = EthereumJsonParser(
        output_folder=args.output,
        max_file_size_mb=args.size,
        file_format=args.format,
        only_heuristic=args.only_heuristic,
    )

    # Start parsing
    ethereum_parser.parse_file(
        file_path=args.input,
        start_block=args.start_block,
        end_block=args.end_block
    )

    ethereum_parser.close()