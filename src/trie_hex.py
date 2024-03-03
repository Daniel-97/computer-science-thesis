import os
import time
from enum import Enum
import datrie
from pathlib import Path

class NodeType(Enum):
    EOA = 1
    SC = 2
    UNK = 3

class Trie:

    def __init__(self) -> None:
        self.datrie = datrie.Trie("0123456789abcdef")
        self.lookup_time = 0

    def add(self, word: str, node_type: NodeType) -> None: 
       self.datrie[word] = node_type
    
    def find_by_type(self, word: str, node_type: NodeType) -> bool:
        return self.find(word) == node_type
    
    def find(self, word: str):
        start_time = time.perf_counter()
        node = None
        try:
            node = self.datrie[word]
        except:
            pass
        
        self.lookup_time += time.perf_counter() - start_time
        return node
    
    def load_trie(self, path: str):
        if os.path.exists(path):
            print(f'Start loading trie from {path}')
            self.datrie = datrie.Trie.load(path)
            print(f'Loaded {len(self.datrie)} nodes from {path} trie')

    def save_trie(self, path: str):
        self.datrie.save(path)
    
            
