from file_splitter_helper import FileSplitterHelper
from abstract_model_parser import AbstractModelParser

class ComplexModelParser(AbstractModelParser):

    def __init__(self,input_file_name: str, output_folder: str, max_file_size_mb: int, file_format: str) -> None:
        out_folder = f'{output_folder}/model1-data'
        # NODES
        self._block_splitter = FileSplitterHelper(f'blocks', f'{out_folder}/nodes/blocks', max_file_size_mb, file_format)
        self._transaction_splitter = FileSplitterHelper(f'txs', f'{out_folder}/nodes/txs', max_file_size_mb, file_format)
        self._eoa_splitter = FileSplitterHelper(f'eoa', f'{out_folder}/nodes/eoa', max_file_size_mb, file_format)
        self._sc_splitter = FileSplitterHelper(f'sc', f'{out_folder}/nodes/sc', max_file_size_mb, file_format)
        self._unk_splitter = FileSplitterHelper(f'unk', f'{out_folder}/nodes/unk', max_file_size_mb, file_format)
        self._log_splitter = FileSplitterHelper(f'log', f'{out_folder}/nodes/log', max_file_size_mb, file_format)

        # REL
        self._sent_splitter = FileSplitterHelper(f'sent', f'{out_folder}/rel/sent', max_file_size_mb, file_format)
        self._contained_splitter = FileSplitterHelper(f'contained', f'{out_folder}/rel/contained', max_file_size_mb, file_format)
        self._transfer_splitter = FileSplitterHelper(f'transfer', f'{out_folder}/rel/transfer', max_file_size_mb, file_format)
        self._creation_splitter = FileSplitterHelper(f'creation', f'{out_folder}/rel/creation', max_file_size_mb, file_format)
        self._invocation_rel_splitter = FileSplitterHelper(f'invocation', f'{out_folder}/rel/invocation', max_file_size_mb, file_format)
        self._emitted_splitter = FileSplitterHelper(f'emitted', f'{out_folder}/rel/emitted', max_file_size_mb, file_format)
        self._unk_rel_splitter = FileSplitterHelper(f'unk', f'{out_folder}/rel/unk', max_file_size_mb, file_format)

    def parse_block(self, block: dict):
        self._block_splitter.append(element=block)
    
    def parse_eoa_transaction(self, transaction: dict):
        self._eoa_splitter.append(element={'address': transaction['fromAddress']})
        self._eoa_splitter.append(element={'address': transaction['toAddress']})
        self._transaction_splitter.append(element=transaction)
        self._transfer_splitter.append(element={'txs': transaction['hash'], 'to': transaction['toAddress']})

    def parse_contract_transaction(self, transaction: dict):
        transaction = transaction.copy()
        logs = transaction.get('logs', [])
        if 'logs' in transaction:
            del transaction['logs']
        self._eoa_splitter.append(element={'address': transaction['fromAddress']})
        self._sc_splitter.append(element={'address': transaction['toAddress']})
        self._transaction_splitter.append(element=transaction)
        self._invocation_rel_splitter.append(element={'txs': transaction['hash'], 'to': transaction['toAddress']})
        self._parse_logs(logs=logs, transaction_hash=transaction['hash'])

    def parse_contract_creation(self, transaction:dict):
        transaction = transaction.copy()
        logs = transaction.get('logs', [])
        if 'logs' in transaction:
            del transaction['logs']
        self._eoa_splitter.append(element={'address': transaction['fromAddress']})
        self._sc_splitter.append(element={'address': transaction['contractAddress']})
        self._transaction_splitter.append(element=transaction)
        self._creation_splitter.append(element={'txs': transaction['hash'], 'to': transaction['contractAddress']})
        self._parse_logs(logs=logs, transaction_hash=transaction['hash'])

    def parse_unknown_transaction(self, transaction: dict):
        self._eoa_splitter.append(element={'address': transaction['fromAddress']})
        self._unk_splitter.append(element={'address': transaction['toAddress']})
        self._transaction_splitter.append(element=transaction)
        self._unk_rel_splitter.append(element={'txs': transaction['hash'], 'to': transaction['toAddress']})

    def _parse_logs(self, logs, transaction_hash):
        for index, log in enumerate(logs):
            log_hash = f'{index}_{transaction_hash}'
            log['hash'] = log_hash
            self._log_splitter.append(element=log)
            self._emitted_splitter.append(element={'transactionHash': transaction_hash,'logHash': log_hash})

    def close_parser(self):
        # Safe close all splitter
        self._block_splitter.end_file()
        self._transaction_splitter.end_file()
        self._eoa_splitter.end_file()
        self._sc_splitter.end_file()
        self._unk_splitter.end_file()
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
        print("- total contract: ", self._sc_splitter.total_row_saved)
        print("- total eoa ", self._eoa_splitter.total_row_saved)
        print("- total logs: ", self._log_splitter.total_row_saved)
        print("- total unknown transactions: ", self._unk_rel_splitter.total_row_saved)