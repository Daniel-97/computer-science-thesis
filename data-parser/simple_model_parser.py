from file_splitter_helper import FileSplitterHelper
import json

class SimpleModelParser:

    def __init__(self, args) -> None:
        out_folder = f'{args.output}/model2-data'
        self._eoa_transaction_splitter = FileSplitterHelper('eoa-transactions', out_folder, args.size, args.format)
        self._contract_transaction_splitter = FileSplitterHelper('contract-transactions', out_folder, args.size, args.format)
        self._contract_creation_splitter = FileSplitterHelper('contract-creation', out_folder, args.size, args.format)
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
        
    def close_parser(self):
        self._eoa_transaction_splitter.end_file()
        self._contract_transaction_splitter.end_file()
        self._contract_creation_splitter.end_file()

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
                #breakpoint()
                transaction['logs_topic'].append(';'.join(log.get('topics','')))
                transaction['logs_data'].append(log.get('data'))
                transaction['logs_block_number'].append(log.get('blockNumber',''))
                transaction['logs_transaction_index'].append(log.get('transactionIndex',''))
                transaction['logs_index'].append(log.get('logIndex',''))
                transaction['logs_type'].append(log.get('@type',''))
                transaction['logs_transaction_hash'].append(log.get('transactionHash',''))