import bz2
import os
import time
import pickle as cPickle
import gc
import sys
from enum import Enum
import datrie
import string

class NodeType(Enum):
    EOA = 0,
    SC = 1

class Trie():

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
            pass
        
        self.lookup_time += time.perf_counter() - start_time
        return found
        
    def save_trie(self):
        self.datrie.save(self.file_name)
    
            
