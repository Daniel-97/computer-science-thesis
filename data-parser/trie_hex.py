import bz2
import os
import time
import pickle as cPickle
import gc
class Node:

    char: str

    def __init__(self, char: str) -> None:
        self.char = char
        self.children: list[Node] = []
        #self.count = 1

class Trie():

    root: Node

    def __init__(self, name: str) -> None:

        self.name = name

        # Load the binary class if present
        if os.path.exists(self._dump_file_name()):
            print(f'Start loading {name} trie from disk...')
            gc.disable()
            with bz2.open(self._dump_file_name(), 'rb') as f:
                self.root = cPickle.load(f)
                print(f"Loaded {f.tell()/1000/1000} MB from {self._dump_file_name()}")
            gc.enable()
        else:
            self.root = Node('')
            
        # STATS
        self.lookup_time = 0
        self.total_nodes = 1
    
    def _dump_file_name(self):
        return f'trie_dump/trie_{self.name}.bz2'
    
    def save_trie(self):
        print(f'Saving {self.name} trie on disk...')
        with bz2.open(self._dump_file_name(), 'wb') as f:
            cPickle.dump(self.root,f)

    def add(self, word: str) -> None: 

        node = self.root

        for char in word:
            
            found_in_child = False

            for child in node.children:
                if child.char == char:
                    node = child
                    found_in_child = True
                    #child.count += 1
                    break

            if not found_in_child:
                new_child = Node(char)
                node.children.append(new_child)
                node = new_child
    
    def find(self, word: str) -> bool:

        start_time = time.perf_counter()
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
        
        self.lookup_time += time.perf_counter() - start_time
        # return true only if it is a child
        return len(node.children) == 0
    
            
