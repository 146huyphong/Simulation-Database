class RadixNode:
    def __init__(self, label="", is_end_of_word=False):
        self.edge_label = label
        self.children = {}
        self.is_end_of_word = is_end_of_word

class CompressTrie:
    def __init__(self):
        self.root = RadixNode()

    def insert(self, word : str):
        current_node = self.root

        while word:

            first_letter = word[0]

            if first_letter not in current_node.children:
                current_node.children[first_letter] = RadixNode(word, True)
                return self
            
            child = current_node.children[first_letter]
            label = child.edge_label 

            i = 0
            for x, y in zip(word, label):
                if x != y:
                    break
                i += 1

            if i == len(label):
                if i == len(word):
                    child.is_end_of_word = True
                    return self
                
                word = word[i:]
                current_node = child
            else:
                split_node = RadixNode(label=label[:i])
                child.edge_label = label[i:]
                split_node.children[label[i]] = child

                if i == len(word):
                    split_node.is_end_of_word = True
                else:
                    new_node = RadixNode(word[i:], True)
                    split_node.children[word[0]] = new_node

                current_node.children[first_letter] = split_node
                return self