from file_splitter_helper import FileSplitterHelper
import json

class SimpleModelParser:

    def __init__(self, args) -> None:
        out_folder = f'{args.output}/model2-data'
        self._eoa_transaction_splitter = FileSplitterHelper('eoa-transactions', out_folder, args.size)
        self._contract_transaction_splitter = FileSplitterHelper('contract-transactions', out_folder, args.size)
        self._contract_creation_splitter = FileSplitterHelper('contract-creation', out_folder, args.size)
        pass

    def parse_eoa_transaction(self, transaction: dict, block: dict):
        block = self._add_dict_prefix(block, 'block')
        transaction = {**transaction, **block}
        self._eoa_transaction_splitter.append(element=json.dumps(transaction))

    def parse_contract_transaction(self, transaction: dict, block: dict):
        block = self._add_dict_prefix(block, 'block')
        transaction = {**transaction, **block}
        self._contract_transaction_splitter.append(element=json.dumps(transaction))

    def parse_contract_creation(self, transaction: dict, block: dict):
        block = self._add_dict_prefix(block, 'block')
        transaction = {**transaction, **block}
        self._contract_creation_splitter.append(element=json.dumps(transaction))
        
    def close_parser(self):
        self._eoa_transaction_splitter.end_file()
        self._contract_transaction_splitter.end_file()
        self._contract_creation_splitter.end_file()


    def _add_dict_prefix(self, dict: dict, prefix: str):
        new_dict = {}
        for key in dict:
            new_dict[f'{prefix}_{key}'] = dict[key]
        
        return new_dict