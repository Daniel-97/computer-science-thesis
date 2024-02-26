from file_splitter_helper import FileSplitterHelper
from abstract_model_parser import AbstractModelParser
from trie_hex import Trie

ACCOUNT_HEADERS = ['account_address', 'account_type']
BLOCK_HEADERS = ['hash','difficulty','extraData','gasLimit','gasUsed','minerAddress','minerType','mixHash','nonce','number','ommerCount','parentHash','receiptsRoot','sha3Uncles','stateRoot','timestamp','totalDifficulty','transactionsRoot']
LOG_HEADERS = ['hash','type','address','blockNumber','data','logIndex','topics','transactionIndex']
TXS_HEADERS = ['hash','blockHash','blockNumber','cumulativeGasUsed','fromAddress','gas','gasPrice','gasUsed','input','nonce','root','status','toAddress','transactionIndex','value', 'contractAddress']

SENT_HEADERS = ['account_address', 'txs_hash']
LOG_HEADER = ['txs_hash', 'log_hash']
CONTAINED_HEADERS = ['txs_hash', 'block_hash']



class ComplexModelParser(AbstractModelParser):

    def __init__(self,input_file_name: str, output_folder: str, max_file_size_mb: int, file_format: str) -> None:
        out_folder = f'{output_folder}/model1-data'
        dump_name = input_file_name.split('_')[0]
        # NODES
        self._block_splitter = FileSplitterHelper(f'{dump_name}-blocks', f'{out_folder}/nodes/', max_file_size_mb, file_format, BLOCK_HEADERS)
        self._transaction_splitter = FileSplitterHelper(f'{dump_name}-txs', f'{out_folder}/nodes/', max_file_size_mb, file_format, TXS_HEADERS)
        self._account_splitter = FileSplitterHelper(f'{dump_name}-account', f'{out_folder}/nodes/', max_file_size_mb, file_format, ACCOUNT_HEADERS)
        self._log_splitter = FileSplitterHelper(f'{dump_name}-log', f'{out_folder}/nodes/', max_file_size_mb, file_format, LOG_HEADERS)

        # REL
        self._sent_splitter = FileSplitterHelper(f'{dump_name}-sent', f'{out_folder}/rel/', max_file_size_mb, file_format, SENT_HEADERS)
        self._contained_splitter = FileSplitterHelper(f'{dump_name}-contained', f'{out_folder}/rel/', max_file_size_mb, file_format, CONTAINED_HEADERS)
        self._transfer_splitter = FileSplitterHelper(f'{dump_name}-transfer', f'{out_folder}/rel/', max_file_size_mb, file_format, SENT_HEADERS)
        self._creation_splitter = FileSplitterHelper(f'{dump_name}-creation', f'{out_folder}/rel/', max_file_size_mb, file_format, SENT_HEADERS)
        self._invocation_rel_splitter = FileSplitterHelper(f'{dump_name}-invocation', f'{out_folder}/rel/', max_file_size_mb, file_format, SENT_HEADERS)
        self._emitted_splitter = FileSplitterHelper(f'{dump_name}-emitted', f'{out_folder}/rel/', max_file_size_mb, file_format, LOG_HEADER)
        self._unk_rel_splitter = FileSplitterHelper(f'{dump_name}-unk', f'{out_folder}/rel/', max_file_size_mb, file_format, SENT_HEADERS)

    def parse_block(self, block: dict):
        self._block_splitter.append(element=block)
    
    def parse_eoa_transaction(self, transaction: dict):
        self._transaction_splitter.append(element=transaction)
        self._transfer_splitter.append(element={'txs_hash': transaction['hash'], 'account_address': transaction['toAddress']})

    def parse_contract_transaction(self, transaction: dict):
        transaction = transaction.copy()
        logs = transaction.get('logs', [])
        if 'logs' in transaction:
            del transaction['logs']
        self._transaction_splitter.append(element=transaction)
        self._invocation_rel_splitter.append(element={'txs_hash': transaction['hash'], 'account_address': transaction['toAddress']})
        self._parse_logs(logs=logs, transaction_hash=transaction['hash'])

    def parse_contract_creation(self, transaction:dict):
        transaction = transaction.copy()
        logs = transaction.get('logs', [])
        if 'logs' in transaction:
            del transaction['logs']
        self._transaction_splitter.append(element=transaction)
        self._creation_splitter.append(element={'txs_hash': transaction['hash'], 'account_address': transaction['contractAddress']})
        self._parse_logs(logs=logs, transaction_hash=transaction['hash'])

    def parse_unknown_transaction(self, transaction: dict):
        self._transaction_splitter.append(element=transaction)
        self._unk_rel_splitter.append(element={'txs_hash': transaction['hash'], 'account_address': transaction['toAddress']})

    def _parse_logs(self, logs, transaction_hash):
        for index, log in enumerate(logs):
            log_hash = f'{index}_{transaction_hash}'
            log['hash'] = log_hash
            if 'topics' not in log:
                log['topics'] = ['-1']
            self._log_splitter.append(element=log)
            self._emitted_splitter.append(element={'txs_hash': transaction_hash,'log_hash': log_hash})

    def parse_trie(self, trie: Trie):
        for key, item in trie.datrie.items():
            self._account_splitter.append(element={'account_address': f'0x{key}', 'account_type': item.value})

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