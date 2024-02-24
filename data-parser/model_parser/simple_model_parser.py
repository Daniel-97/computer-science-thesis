from file_splitter_helper import FileSplitterHelper
from abstract_model_parser import AbstractModelParser

class SimpleModelParser(AbstractModelParser):

    def __init__(self, input_file_name:str, output_folder: str, max_file_size_mb: int, file_format: str) -> None:
        out_folder = f'{output_folder}/model2-data'
        dump_name = input_file_name.split('_')[0]
        self._eoa_splitter = FileSplitterHelper(f'{dump_name}-eoa', f'{out_folder}/nodes/', max_file_size_mb, file_format)
        self._sc_splitter = FileSplitterHelper(f'{dump_name}-sc', f'{out_folder}/nodes/', max_file_size_mb, file_format)
        self._unk_splitter = FileSplitterHelper(f'{dump_name}-unk', f'{out_folder}/nodes/', max_file_size_mb, file_format)
        self._transfer_splitter = FileSplitterHelper(f'{dump_name}-transfer', f'{out_folder}/rel/', max_file_size_mb, file_format)
        self._invocation_splitter = FileSplitterHelper(f'{dump_name}-invocation', f'{out_folder}/rel/', max_file_size_mb, file_format)
        self._creation_splitter = FileSplitterHelper(f'{dump_name}-creation', f'{out_folder}/rel/', max_file_size_mb, file_format)
        self._unk_rel_splitter = FileSplitterHelper(f'{dump_name}-unk', f'{out_folder}/rel/', max_file_size_mb, file_format)

    def parse_block(self, block: dict):
        pass
    
    def parse_eoa_transaction(self, transaction: dict, block: dict):
        block = self._add_dict_prefix(dict=block,prefix='block')
        transaction = {**transaction, **block}

        self._eoa_splitter.append(element={'address': transaction['fromAddress']})
        self._eoa_splitter.append(element={'address': transaction['toAddress']})
        self._transfer_splitter.append(element=transaction)

    def parse_contract_transaction(self, transaction: dict, block: dict):
        transaction = transaction.copy()
        block = self._add_dict_prefix(dict=block, prefix='block')
        transaction = {**transaction, **block}
        self._flatten_logs(transaction)
        self._eoa_splitter.append(element={'address': transaction['fromAddress']})
        self._sc_splitter.append(element={'address': transaction['toAddress']})
        self._invocation_splitter.append(element=transaction)

    def parse_contract_creation(self, transaction: dict, block: dict):
        transaction = transaction.copy()
        block = self._add_dict_prefix(dict=block,prefix='block')
        transaction = {**transaction, **block}
        self._flatten_logs(transaction)
        self._eoa_splitter.append(element={'address': transaction['fromAddress']})
        self._sc_splitter.append(element={'address': transaction['contractAddress']})
        self._creation_splitter.append(element=transaction)

    def parse_unknown_transaction(self, transaction: dict, block: dict):
        block = self._add_dict_prefix(dict=block,prefix='block')
        transaction = {**transaction, **block}
        self._eoa_splitter.append(element={'address': transaction['fromAddress']})
        self._unk_splitter.append(element={'address': transaction['toAddress']})
        self._unk_rel_splitter.append(element=transaction)

    def close_parser(self):
        self._eoa_splitter.end_file()
        self._sc_splitter.end_file()
        self._unk_splitter.end_file()
        self._transfer_splitter.end_file()
        self._invocation_splitter.end_file()
        self._creation_splitter.end_file()
        self._unk_rel_splitter.end_file()

        print("\nModel 2 (simple) stats:")
        print("- total EOA address: ", self._eoa_splitter.total_row_saved)
        print("- total SC address: ", self._sc_splitter.total_row_saved)
        print("- total UNK address: ", self._unk_splitter.total_row_saved)
        print("- total transfer transaction: ", self._transfer_splitter.total_row_saved)
        print("- total invocation transaction: ", self._invocation_splitter.total_row_saved)
        print("- total creation transaction: ", self._creation_splitter.total_row_saved)
        print("- total unk transaction: ", self._unk_rel_splitter.total_row_saved)

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