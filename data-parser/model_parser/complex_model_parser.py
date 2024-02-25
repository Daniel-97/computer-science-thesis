from file_splitter_helper import FileSplitterHelper
from abstract_model_parser import AbstractModelParser
from trie_hex import Trie

class ComplexModelParser(AbstractModelParser):

    def __init__(self,input_file_name: str, output_folder: str, max_file_size_mb: int, file_format: str) -> None:
        out_folder = f'{output_folder}/model1-data'
        dump_name = input_file_name.split('_')[0]
        # NODES
        self._block_splitter = FileSplitterHelper(f'{dump_name}-blocks', f'{out_folder}/nodes/', max_file_size_mb, file_format)
        self._transaction_splitter = FileSplitterHelper(f'{dump_name}-txs', f'{out_folder}/nodes/', max_file_size_mb, file_format)
        self._account_splitter = FileSplitterHelper(f'{dump_name}-account', f'{out_folder}/nodes/', max_file_size_mb, file_format)
        self._log_splitter = FileSplitterHelper(f'{dump_name}-log', f'{out_folder}/nodes/', max_file_size_mb, file_format)

        # REL
        self._sent_splitter = FileSplitterHelper(f'{dump_name}-sent', f'{out_folder}/rel/', max_file_size_mb, file_format)
        self._contained_splitter = FileSplitterHelper(f'{dump_name}-contained', f'{out_folder}/rel/', max_file_size_mb, file_format)
        self._transfer_splitter = FileSplitterHelper(f'{dump_name}-transfer', f'{out_folder}/rel/', max_file_size_mb, file_format)
        self._creation_splitter = FileSplitterHelper(f'{dump_name}-creation', f'{out_folder}/rel/', max_file_size_mb, file_format)
        self._invocation_rel_splitter = FileSplitterHelper(f'{dump_name}-invocation', f'{out_folder}/rel/', max_file_size_mb, file_format)
        self._emitted_splitter = FileSplitterHelper(f'{dump_name}-emitted', f'{out_folder}/rel/', max_file_size_mb, file_format)
        self._unk_rel_splitter = FileSplitterHelper(f'{dump_name}-unk', f'{out_folder}/rel/', max_file_size_mb, file_format)

    def parse_block(self, block: dict):
        self._block_splitter.append(element=block)
    
    def parse_eoa_transaction(self, transaction: dict):
        self._transaction_splitter.append(element=transaction)
        self._transfer_splitter.append(element={'txs': transaction['hash'], 'to': transaction['toAddress']})

    def parse_contract_transaction(self, transaction: dict):
        transaction = transaction.copy()
        logs = transaction.get('logs', [])
        if 'logs' in transaction:
            del transaction['logs']
        self._transaction_splitter.append(element=transaction)
        self._invocation_rel_splitter.append(element={'txs': transaction['hash'], 'to': transaction['toAddress']})
        self._parse_logs(logs=logs, transaction_hash=transaction['hash'])

    def parse_contract_creation(self, transaction:dict):
        transaction = transaction.copy()
        logs = transaction.get('logs', [])
        if 'logs' in transaction:
            del transaction['logs']
        self._transaction_splitter.append(element=transaction)
        self._creation_splitter.append(element={'txs': transaction['hash'], 'to': transaction['contractAddress']})
        self._parse_logs(logs=logs, transaction_hash=transaction['hash'])

    def parse_unknown_transaction(self, transaction: dict):
        self._transaction_splitter.append(element=transaction)
        self._unk_rel_splitter.append(element={'txs': transaction['hash'], 'to': transaction['toAddress']})

    def _parse_logs(self, logs, transaction_hash):
        for index, log in enumerate(logs):
            log_hash = f'{index}_{transaction_hash}'
            log['hash'] = log_hash
            self._log_splitter.append(element=log)
            self._emitted_splitter.append(element={'transactionHash': transaction_hash,'logHash': log_hash})

    def parse_trie(self, trie: Trie):
        for key, item in trie.datrie.items():
            self._account_splitter.append(element={'address': key, 'account_type': item.value})

    def close_parser(self):
        # Safe close all splitter
        self._block_splitter.end_file()
        self._transaction_splitter.end_file()
        self._account_splitter.end_file()
        self._sent_splitter.end_file()
        self._contained_splitter.end_file()
        self._transfer_splitter.end_file()
        self._creation_splitter.end_file()
        self._invocation_rel_splitter.end_file()
        self._emitted_splitter.end_file()
        self._unk_rel_splitter.end_file()

        print("\nModel 1 (complex) stats:")
        print("- total blocks: ", self._block_splitter.total_row_saved)
        print("- total transactions: ", self._transaction_splitter.total_row_saved)
        print("- total address: ", self._account_splitter.total_row_saved)
        print("- total logs: ", self._log_splitter.total_row_saved)
        print("- total unknown transactions: ", self._unk_rel_splitter.total_row_saved)