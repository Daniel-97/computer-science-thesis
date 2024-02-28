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

    def __init__(self, name: str) -> None:
        self.name = name
        self.file_name = f'trie_dump/datrie-{name}.trie'
        self.datrie = datrie.Trie("0123456789abcdef")
        self.lookup_time = 0
        if os.path.exists(self.file_name):
            print(f'Start loading trie {name}')
            self.datrie = datrie.Trie.load(self.file_name)
            print(f'Loaded {len(self.datrie)} nodes from {name} trie')

    def add(self, word: str, node_type: NodeType) -> None: 
       self.datrie[word] = node_type
    
    def find(self, word: str, node_type: NodeType) -> bool:

        start_time = time.perf_counter()
        found = False
        try:
            found = self.datrie[word] == node_type
        except:
            found = False
        
        self.lookup_time += time.perf_counter() - start_time
        return found
        
    def save_trie(self):
        Path('trie_dump').mkdir(parents=True, exist_ok=True)
        self.datrie.save(self.file_name)
    
            
