from file_splitter_helper import FileSplitterHelper
import json

class SimpleModelParser:

    def __init__(self, args) -> None:
        out_folder = f'{args.output}/model2-data'
        self._eoa_transaction_splitter = FileSplitterHelper('eoa-transactions', out_folder, args.size, args.format)
        self._contract_transaction_splitter = FileSplitterHelper('contract-transactions', out_folder, args.size, args.format)
        self._contract_creation_splitter = FileSplitterHelper('contract-creation', out_folder, args.size, args.format)
        self._unknown_transaction_splitter = FileSplitterHelper('unknown-transactions', out_folder, args.size, args.format)

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

        print("Model 2 (simple) stats:")
        print("- total EOA transaction: ", self._eoa_transaction_splitter.total_row_saved)
        print("- total contract transaction: ", self._contract_transaction_splitter.total_row_saved)
        print("- total contract creation transaction: ", self._contract_creation_splitter.total_row_saved)

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
                transaction['logs_topic'].append(','.join(topics))
                transaction['logs_data'].append(log.get('data'))
                transaction['logs_block_number'].append(log.get('blockNumber',''))
                transaction['logs_transaction_index'].append(log.get('transactionIndex',''))
                transaction['logs_index'].append(log.get('logIndex',''))
                transaction['logs_type'].append(log.get('@type',''))
                transaction['logs_transaction_hash'].append(log.get('transactionHash',''))