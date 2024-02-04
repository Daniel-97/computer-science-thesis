from typing import Tuple
import pickle
import bz2
import os

class Node:

    char: str

    def __init__(self, char: str) -> None:
        self.char = char
        self.children: list[Node] = []
        self.count = 1

class Trie():

    root: Node

    def __init__(self, name: str) -> None:

        self.name = name

        # Load the binary class if present
        if os.path.exists(self._trie_dump_file_name()):
            with bz2.open(self._trie_dump_file_name(), 'rb') as f:
                self.root = pickle.load(f)
                print(f"Loaded {f.tell()} bytes from {self._trie_dump_file_name()}")
        else:
            self.root = Node('')
    
    def _trie_dump_file_name(self):
        return f'trie_dump/trie_{self.name}.bz2'
    
    def save_trie(self):
        with bz2.open(self._trie_dump_file_name(), 'wb') as f:
            pickle.dump(self.root,f,pickle.HIGHEST_PROTOCOL)

    def add(self, word: str) -> None: 

        node = self.root

        for char in word:
            
            found_in_child = False

            for child in node.children:
                if child.char == char:
                    node = child
                    found_in_child = True
                    child.count += 1
                    break

            if not found_in_child:
                new_child = Node(char)
                node.children.append(new_child)
                node = new_child

    def find_prefix(self, prefix: str) -> Tuple[bool, int]:

        node = self.root

        if not node.children:
            return False, 0
        
        for char in prefix:
            char_found = False
            for child in node.children:
                if child.char == char:
                    node = child
                    char_found = True
                    break

            if not char_found:
                return False, 0
            
        return True, node.count
    
    def find(self, word: str) -> bool:

        node = self.root

        if not node.children:
            return False
        
        for char in word:
            char_found = False
            for child in node.children:
                if child.char == char:
                    node = child
                    char_found = True
                    break

            if not char_found:
                return False
        
        # return true only if it is a child
        return len(node.children) == 0
    
            
