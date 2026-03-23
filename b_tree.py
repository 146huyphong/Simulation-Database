class Student:
    def __init__(self, student_id, name, gender):
        self.student_id = student_id
        self.name = name
        self.gender = gender
        self.staus = 'active'
    

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

    def to_dict(self):
        keys_str = ",".join(str(k) for k in self.keys)

        node_dict = {
            "name": f"[{keys_str}]",
            "keys": self.keys,
            "offsets": self.offsets,
            "leaf": self.leaf,
        }

        if not self.leaf and self.children:
            node_dict["children"] = [child.to_dict() for child in self.children]
        
        return node_dict

class BTree:
    def __init__(self, t = 3):
        self.root = BTreeNode(leaf=True)
        self.max_keys = t - 1
        self.min_keys = self.max_keys >> 1

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
    
    def insert(self, key, offset):
        split_data = self._insert_non_full(self.root, key, offset)

        if split_data is not None:
            new_root = BTreeNode(leaf=False)
            new_root.keys = [split_data['key']]
            new_root.offsets = [split_data['offset']]
            new_root.children = [self.root, split_data['right_node']]
            self.root = new_root

    
    
    def _insert_non_full(self, node, key, offset):
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1

        if node.leaf:
            node.keys.insert(i, key)
            node.offsets.insert(i, offset)
        else:
            split_data = self._insert_non_full(node.children[i], key, offset)

            if split_data is not None:
                node.keys.insert(i, split_data['key'])
                node.offsets.insert(i, split_data['offset'])
                node.children.insert(i + 1, split_data['right_node'])

        if len(node.keys) > self.max_keys:
            return self._split_node(node)
        
        return None


    def _split_node(self, node):
        mid_index = (len(node.keys)) >> 1

        mid_key = node.keys[mid_index]
        mid_offset = node.offsets[mid_index]

        right_node = BTreeNode(leaf=node.leaf)
        right_node.keys = node.keys[mid_index + 1:]
        right_node.offsets = node.offsets[mid_index + 1:]

        if not node.leaf:
            right_node.children = node.children[mid_index + 1:]
            node.children = node.children[:mid_index + 1]
        
        node.keys = node.keys[:mid_index]
        node.offsets = node.offsets[:mid_index]

        return {
            'key': mid_key,
            'offset': mid_offset,
            'right_node': right_node
        }

    def delete(self, key):
        if not self.root.keys:
            return False

        is_deleted = self._delete_recursive(self.root, key)      

        if len(self.root.keys) == 0 and not self.root.leaf:
            self.root = self.root.children[0]

        return is_deleted  

    def _delete_recursive(self, node, key):
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1

        if i < len(node.keys) and key == node.keys[i]:
            if node.leaf:
                node.keys.pop(i)
                node.offsets.pop(i)
                return True
            else:
                pred_node = self._get_max_node(node.children[i])
                pred_key = pred_node.keys[-1]
                pred_offset = pred_node.offsets[-1]

                node.keys[i] = pred_key
                node.offsets[i] = pred_offset

                is_deleted = self._delete_recursive(node.children[i], pred_key)
        else:
            if node.leaf:
                return False
            
            is_deleted = self._delete_recursive(node.children[i], key)

        if not node.leaf and len(node.children[i].keys) < self.min_keys:
            self._fix_underflow(node, i)

        return is_deleted
    
    def _get_max_node(self, node):
        current = node

        while not current.leaf:
            current = current.children[-1]
        return current
    
    def _fix_underflow(self, parent, index):
        child = parent.children[index]

        if index > 0 and len(parent.children[index - 1].keys) > self.min_keys:
            left_sibling = parent.children[index - 1]
            
            child.keys.insert(0, parent.keys[index - 1])
            child.offsets.insert(0, parent.offsets[index - 1])
            
            parent.keys[index - 1] = left_sibling.keys.pop(-1)
            parent.offsets[index - 1] = left_sibling.offsets.pop(-1)

            if not child.leaf:
                child.children.insert(0, left_sibling.children.pop(-1))

            return
        
        if index < len(parent.children) - 1 and len(parent.children[index + 1].keys) > self.min_keys:
            right_sibling = parent.children[index + 1]

            child.keys.append(parent.keys[index])
            child.offsets.append(parent.offsets[index])

            parent.keys[index] = right_sibling.keys.pop(0)
            parent.offsets[index] = right_sibling.offsets.pop(0)

            if not child.leaf:
                child.children.append(right_sibling.children.pop(0))
            
            return 
        
        if index > 0:
            self._merge_nodes(parent, index - 1)
        else:
            self._merge_nodes(parent, index)

    def _merge_nodes(self, parent, index):  
        left_child = parent.children[index]
        right_child = parent.children[index + 1]

        left_child.keys.append(parent.keys.pop(index))
        left_child.offsets.append(parent.offsets.pop(index))

        left_child.keys.extend(right_child.keys)
        left_child.offsets.extend(right_child.offsets)

        if not left_child.leaf:
            left_child.children.extend(right_child.children)

        parent.children.pop(index + 1)  

    def get_tree_state(self):
        if not self.root.keys:
            return {}
        
        return self.root.to_dict()