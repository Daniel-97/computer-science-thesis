from typing import Tuple

class Node:

    char: str

    def __init__(self, char: str) -> None:
        self.char = char
        self.children: list[Node] = []
        self.count = 1

class Trie():

    root: Node

    def __init__(self) -> None:
        self.root = Node('')

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
            return False, 0
        
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
    
            
