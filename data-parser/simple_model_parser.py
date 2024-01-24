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
        tx_copy = transaction.copy()

        block = self._add_dict_prefix(dict=block, prefix='block')
        tx_copy = {**tx_copy, **block}

        if 'logs' in tx_copy:
            logs = tx_copy.get('logs', [])
            del tx_copy['logs']
            for index, log in enumerate(logs):
                log = self._add_dict_prefix(dict=log, prefix=f'log_{index}')
                tx_copy = {**tx_copy, **log}

        self._contract_transaction_splitter.append(element=tx_copy)

    def parse_contract_creation(self, transaction: dict, block: dict):
        block = self._add_dict_prefix(dict=block,prefix='block')
        transaction = {**transaction, **block}
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