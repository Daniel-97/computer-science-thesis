from dataclasses import dataclass
import json

@dataclass
class Transaction:
    hash: str
    blockNumber: str
    gas: str
    gasPrice: str
    input: str
    nonce: str
    value: str
    cumulativeGasUsed: str
    gasUsed: str
    status: str
    type: str
    from_type: str
    from_address: str
    to_type: str
    to_address: str
    #TODO qui mancano i log che sono dati molto importanti per i token transfer

    def __init__(self, json_dict: dict):
        self.hash = json_dict['hash']
        self.blockNumber = json_dict['blockNumber']
        self.gas = json_dict['gas']
        self.gasPrice = json_dict['gasPrice']
        self.input = json_dict['input']
        self.nonce = json_dict['nonce']
        self.value = json_dict['value']
        self.type = json_dict['type']
        self.cumulativeGasUsed = json_dict['cumulativeGasUsed']
        self.gasUsed = json_dict['gasUsed']
        self.status = json_dict['status']
        self.type = json_dict['@type']

        if 'from' in json_dict:
            self.from_type = json_dict['from'].get('@type')
            self.from_address = json_dict['from'].get('address')
        
        if 'to' in json_dict:
            self.to_type = json_dict['to'].get('@type')
            self.to_address = json_dict['to'].get('address')
