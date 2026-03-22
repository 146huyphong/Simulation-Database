class Student:
    def __int__(self, student_id, name, gender):
        self.student_id = student_id
        self.name = name
        self.gender = gender
    

    def to_dict(self):
        return {
            'student_id': self.student_id,
            'name': self.name,
            'gender': self.gender,
            'status': 'active' if not self.is_deleted else 'deleted'
        }
    
class BTreeNode:
    def __init__(self, leaf=False):
        self.leaf = leaf
        self.keys = []
        self.offsets = []
        self.children = []

class BTree:
    def __init__(self, t = 3):
        self.root = BTreeNode(leaf=True)
        self.t = t  

    def search(self, key, node=None):
        if node is None:
            node = self.root

        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1

        if i < len(node.keys) and key == node.keys[i]:
            return node.offsets[i]
        
        if node.leaf:
            return None
        
        return self.search(key, node.children[i])
    
    def _split_node(self, node):
        mid_index = self.m << 1

        mid_key = node.keys[mid_index]
        mid_offset = node.offsets[mid_index]

        right_node = BTreeNode(leaf=node.leaf)
        right_node.keys = node.keys[mid_index + 1:]
        right_node.offsets = node.offsets[:mid_index]

        if not node.leaf:
            right_node.children = node.children[mid_index + 1:]
            node.children = node.childre[:mid_index + 1]
        
        node.keys = node.keys[:mid_index]
        node.offsets = node.offsets[:mid_index]

        return {
            'key': mid_key,
            'offset': mid_offset,
            'right_node': right_node
        }

    def insert_non_full(self, node, key, offset):
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1

        if node.leaf:
            node.keys.insert(i, key)
            node.offsets.insert(i, offset)
        else:
            split_data = self.insert_non_full(node.children[i], key, offset)

            if split_data is not None:
                node.keys.insert(i, split_data['key'])
                node.offsets.insert(i, split_data['offset'])
                node.children.insert(i + 1, split_data['new_node'])

        if len(node.keys) == self.m:
            return self._split_node(node)
        
        return None

    def insert(self, key, offset):
        split_data = self.insert_non_full(self.root, key, offset)

    def delete(self, key):
        pass

    def get_tree_state(self):
        pass