from file_splitter_helper import FileSplitterHelper
import json

class ComplexModelParser:

    def __init__(self, args) -> None:
        # Splitter
        out_folder = f'{args.output}/model1-data/'
        self._block_splitter = FileSplitterHelper('blocks', out_folder, args.size)
        self._eoa_transaction_splitter = FileSplitterHelper('eoa-transactions', out_folder, args.size)
        self._contract_transaction_splitter = FileSplitterHelper('contract-transactions', out_folder, args.size)
        self._contract_creation_splitter = FileSplitterHelper('contract-creation', out_folder, args.size)
        self._log_splitter = FileSplitterHelper('contract-logs', out_folder, args.size)

    def parse_block(self, block: dict):
        self._block_splitter.append(element=json.dumps(block))
    
    def parse_eoa_transaction(self, transaction: dict):
        self._eoa_transaction_splitter.append(element=json.dumps(transaction))
        pass

    def parse_contract_transaction(self, transaction: dict):
        logs = transaction.get('logs', [])
        if 'logs' in transaction:
            del transaction['logs']
        self._contract_transaction_splitter.append(element=json.dumps(transaction))
        for log in logs:
            log['transactionHash'] = transaction['hash']
            self._log_splitter.append(element=json.dumps(log))

    def parse_contract_creation(self, transaction:dict):
        self._contract_creation_splitter.append(element=json.dumps(transaction))

    def close_parser(self):
        # Safe close all splitter
        self._block_splitter.end_file()
        self._eoa_transaction_splitter.end_file()
        self._contract_transaction_splitter.end_file()
        self._contract_creation_splitter.end_file()
        self._log_splitter.end_file()