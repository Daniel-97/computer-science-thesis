import bz2
import os
import time
import pickle as cPickle
import gc
import sys
class Node:

    char: str

    def __init__(self, char: str) -> None:
        self.char = char
        self.children: list[Node] = []
        #self.count = 1

class Trie():

    root: Node

    @staticmethod
    def load_instance(trie_name: str):
         # Load the binary class if present
        if os.path.exists(Trie.dump_file_name(trie_name)):
            print(f'Start loading {trie_name} trie from disk...')
            gc.disable()
            with bz2.open(Trie.dump_file_name(trie_name), 'rb') as f:
                instance = cPickle.load(f)
                print(f"Loaded {f.tell()/1000/1000} MB from {Trie.dump_file_name(trie_name)}. Total nodes: {instance.total_nodes}")
                print(sys.getsizeof(instance.root))
            gc.enable()
            return instance
        else:
            return Trie(trie_name)

    @staticmethod
    def dump_file_name(name: str) -> str:
        return f'trie_dump/trie_{name}.bz2'
    
    @staticmethod
    def save_trie(trie_instance):
        print(f'Saving {trie_instance.name} trie on disk...')
        with bz2.open(Trie.dump_file_name(trie_instance.name), 'wb') as f:
            cPickle.dump(trie_instance,f)

    def __init__(self, name: str) -> None:

        self.name = name
        self.root = Node('')

        # STATS
        self.lookup_time = 0
        self.total_nodes = 1

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
                self.total_nodes += 1
    
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
    
            
