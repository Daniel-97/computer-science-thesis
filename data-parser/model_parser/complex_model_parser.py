from file_splitter_helper import FileSplitterHelper
from abstract_model_parser import AbstractModelParser

class ComplexModelParser(AbstractModelParser):

    def __init__(self, args) -> None:
        # Splitter
        out_folder = f'{args.output}/model1-data'
        self._block_splitter = FileSplitterHelper('blocks', out_folder, args.size, args.format)
        self._eoa_transaction_splitter = FileSplitterHelper('eoa-transactions', out_folder, args.size, args.format)
        self._contract_transaction_splitter = FileSplitterHelper('contract-transactions', out_folder, args.size, args.format)
        self._contract_creation_splitter = FileSplitterHelper('contract-creation', out_folder, args.size, args.format)
        self._log_splitter = FileSplitterHelper('contract-logs', out_folder, args.size, args.format)
        self._unknown_transaction_splitter = FileSplitterHelper('unknown-transactions', out_folder, args.size, args.format)

    def parse_block(self, block: dict):
        self._block_splitter.append(element=block)
    
    def parse_eoa_transaction(self, transaction: dict):
        self._eoa_transaction_splitter.append(element=transaction)

    def parse_contract_transaction(self, transaction: dict):
        transaction = transaction.copy()
        logs = transaction.get('logs', [])

        if 'logs' in transaction:
            del transaction['logs']
        self._contract_transaction_splitter.append(element=transaction)

        for log in logs:
            log['transactionHash'] = transaction['hash']
            self._log_splitter.append(element=log)

    def parse_contract_creation(self, transaction:dict):
        transaction = transaction.copy()
        logs = transaction.get('logs', [])

        if 'logs' in transaction:
            del transaction['logs']
        self._contract_creation_splitter.append(element=transaction)

        for log in logs:
            log['transactionHash'] = transaction['hash']
            self._log_splitter.append(element=log)

    def parse_unknown_transaction(self, transaction: dict):
        self._unknown_transaction_splitter.append(element=transaction)

    def close_parser(self):
        # Safe close all splitter
        self._block_splitter.end_file()
        self._eoa_transaction_splitter.end_file()
        self._contract_transaction_splitter.end_file()
        self._contract_creation_splitter.end_file()
        self._log_splitter.end_file()
        self._unknown_transaction_splitter.end_file()

        print("\nModel 1 (complex) stats:")
        print("- total blocks: ", self._block_splitter.total_row_saved)
        print("- total EOA transactions: ", self._eoa_transaction_splitter.total_row_saved)
        print("- total contract transactions: ", self._contract_transaction_splitter.total_row_saved)
        print("- total contract creation transactions: ", self._contract_creation_splitter.total_row_saved)
        print("- total logs: ", self._log_splitter.total_row_saved)
        print("- total unknown transactions: ", self._unknown_transaction_splitter.total_row_saved)