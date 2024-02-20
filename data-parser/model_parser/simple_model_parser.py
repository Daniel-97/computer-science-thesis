from file_splitter_helper import FileSplitterHelper
from abstract_model_parser import AbstractModelParser

class SimpleModelParser(AbstractModelParser):

    def __init__(self, input_file_name:str, output_folder: str, max_file_size_mb: int, file_format: str) -> None:
        out_folder = f'{output_folder}/model2-data'
        self._eoa_transaction_splitter = FileSplitterHelper(f'{input_file_name}-eoa-txs', f'{out_folder}/eoa-txs', max_file_size_mb, file_format)
        self._contract_transaction_splitter = FileSplitterHelper(f'{input_file_name}-sc-txs', f'{out_folder}/sc-txs', max_file_size_mb, file_format)
        self._contract_creation_splitter = FileSplitterHelper(f'{input_file_name}-sc-creation', f'{out_folder}/sc-creation', max_file_size_mb, file_format)
        self._unknown_transaction_splitter = FileSplitterHelper(f'{input_file_name}-unk-txs', f'{out_folder}/unk-txs', max_file_size_mb, file_format)

    def parse_block(self, block: dict):
        pass
    
    def parse_eoa_transaction(self, transaction: dict, block: dict):
        block = self._add_dict_prefix(dict=block,prefix='block')
        transaction = {**transaction, **block}
        self._eoa_transaction_splitter.append(element=transaction)

    def parse_contract_transaction(self, transaction: dict, block: dict):
        transaction = transaction.copy()

        block = self._add_dict_prefix(dict=block, prefix='block')
        transaction = {**transaction, **block}

        self._flatten_logs(transaction)

        self._contract_transaction_splitter.append(element=transaction)

    def parse_contract_creation(self, transaction: dict, block: dict):
        transaction = transaction.copy()

        block = self._add_dict_prefix(dict=block,prefix='block')
        transaction = {**transaction, **block}

        self._flatten_logs(transaction)

        self._contract_creation_splitter.append(element=transaction)

    def parse_unknown_transaction(self, transaction: dict, block: dict):
        block = self._add_dict_prefix(dict=block,prefix='block')
        transaction = {**transaction, **block}
        self._unknown_transaction_splitter.append(element=transaction)

    def close_parser(self):
        self._eoa_transaction_splitter.end_file()
        self._contract_transaction_splitter.end_file()
        self._contract_creation_splitter.end_file()
        self._unknown_transaction_splitter.end_file()

        print("\nModel 2 (simple) stats:")
        print("- total EOA transactions: ", self._eoa_transaction_splitter.total_row_saved)
        print("- total contract transactions: ", self._contract_transaction_splitter.total_row_saved)
        print("- total contract creation transactions: ", self._contract_creation_splitter.total_row_saved)
        print("- total unknown transactions: ", self._unknown_transaction_splitter.total_row_saved)

    def _add_dict_prefix(self, dict: dict, prefix: str):
        new_dict = {}
        for key in dict:
            new_dict[f'{prefix}_{key}'] = dict[key]
        
        return new_dict

    def _flatten_logs(self, transaction: dict):
        """
            This function flat the information of the logs in some parallel array
        """

        transaction['logs_address'] = []
        transaction['logs_topic'] = []
        transaction['logs_data'] = []
        transaction['logs_block_number'] = []
        transaction['logs_transaction_index'] = []
        transaction['logs_index'] = []
        transaction['logs_type'] = []
        transaction['logs_transaction_hash'] = []
        
        if 'logs' in transaction:
            logs = transaction['logs']
            del transaction['logs']

            for log in logs:
                transaction['logs_address'].append(log.get('address',''))
                # Non posso memorizzare array di array, ma so che i topics possono essere al massimo 3. 
                # Quindi li metto tutti nello stesso array parallelo, e quindi so che i primi 3 sono del primo log
                # i secondi 3 del secondo log e cosi via. Se trovo -1 non ho topic in quella posizione
                topics = ['-1','-1','-1', '-1']
                for index, topic in enumerate(log.get('topics', [])):
                    topics[index] = topic
                transaction['logs_topic'].append('|'.join(topics))
                transaction['logs_data'].append(log.get('data'))
                transaction['logs_block_number'].append(log.get('blockNumber',''))
                transaction['logs_transaction_index'].append(log.get('transactionIndex',''))
                transaction['logs_index'].append(log.get('logIndex',''))
                transaction['logs_type'].append(log.get('@type',''))
                transaction['logs_transaction_hash'].append(log.get('transactionHash',''))