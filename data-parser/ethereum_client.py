import requests
import json

class EthereumClient:

    BASE_URL = 'https://palpable-old-gadget.quiknode.pro/e42303fa90a4a8a351571568ddbb99adb1e4262d/'
    HEADERS = {'ContentType': 'application/json'}

    def __init__(self) -> None:
        pass

    def eth_getCode(self, address: str):
        payload = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_getCode",
            "params": [
                address,
                "latest"
            ]
        })

        response = requests.request(method="POST", url=self.BASE_URL, headers=self.HEADERS, data=payload)
        return response.json()
    
    def eth_getAccount(self, address: str):
        payload = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_getAccount",
            "params": [
                address,
                "latest"
            ]
        })

        response = requests.request(method="POST", url=self.BASE_URL, headers=self.HEADERS, data=payload)
        return response.json()
    
    def is_contract(self, address: str):

        code_response = self.eth_getCode(address=address)

        if code_response['result'] != '0x':
            return True

        else:
            account_response = self.eth_getAccount(address=address)
            
            # If no info are present in the latest block for the address, it means it is a SC self destructed
            if account_response['result'] is None:
                return True
            else:
                return False