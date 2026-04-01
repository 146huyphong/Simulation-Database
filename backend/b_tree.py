class Student:
    """
    Lớp đại diện cho thực thể Sinh viên trong hệ thống.
    """
    def __init__(self, student_id, name, gender):
        """
        Khởi tạo đối tượng Sinh viên.

        Args:
            student_id (str): Mã số sinh viên.
            name (str): Họ và tên sinh viên.
            gender (str): Giới tính của sinh viên.
        """
        self.student_id = student_id
        self.name = name
        self.gender = gender
        self.status = 'active'
        self.is_deleted = False

    def to_dict(self):
        """
        Chuyển đổi thông tin sinh viên thành cấu trúc từ điển (dictionary).

        Returns:
            dict: Từ điển chứa các thuộc tính của sinh viên để dễ dàng chuyển đổi sang JSON.
        """
        return {
            'student_id': self.student_id,
            'name': self.name,
            'gender': self.gender,
            'status': 'active' if not self.is_deleted else 'deleted'
        }
    

class BTreeNode:
    """
    Lớp đại diện cho một node bên trong cấu trúc cây B-Tree.
    """
    def __init__(self, leaf=False):
        """
        Khởi tạo một nút mới trong cây B-Tree.

        Args:
            leaf (bool): Xác định xem nút này có phải là nút lá hay không. Mặc định là False.
        """
        self.leaf = leaf
        self.keys = []
        self.offsets = [] 
        self.children = []

    def to_dict(self):
        """
        Biểu diễn cấu trúc của nút dưới dạng từ điển.

        Returns:
            dict: Biểu diễn phân cấp của nút.
        """
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
    """
    Lớp cài đặt cấu trúc dữ liệu cây B-Tree để tạo chỉ mục tìm kiếm.
    """
    def __init__(self, t=3):
        """
        Khởi tạo cây B-Tree.

        Args:
            t (int): Bậc của cây B-Tree. Quy định số lượng khóa tối đa và tối thiểu trong mỗi nút.
        """
        self.root = BTreeNode(leaf=True)
        self.max_keys = t - 1
        self.min_keys = self.max_keys >> 1

    def search(self, key, node=None):
        """
        Tìm kiếm một key bên trong cây B-Tree.

        Args:
            key: Khóa cần tìm kiếm (có thể là MSSV hoặc Họ tên).
            node (BTreeNode, optional): Nút bắt đầu tìm kiếm. Nếu bỏ trống sẽ bắt đầu từ nút gốc.

        Returns:
            list hoặc None: Trả về danh sách các offsets nếu tìm thấy, ngược lại trả về None.
        """
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
    
    def _add_offset_if_exists(self, node, key, offset):
        """
        Kiểm tra và xử lý trường hợp khóa trùng lặp.
        Nếu khóa đã tồn tại trong cây, chỉ cần thêm địa chỉ vật lý (offset) mới vào danh sách.

        Args:
            node (BTreeNode): Nút đang xét.
            key: Khóa cần kiểm tra.
            offset (int): Địa chỉ vật lý cần thêm.

        Returns:
            bool: True nếu khóa đã tồn tại và đã thêm offset, False nếu khóa chưa tồn tại.
        """
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if i < len(node.keys) and key == node.keys[i]:
            if offset not in node.offsets[i]:
                node.offsets[i].append(offset)
            return True
        if node.leaf:
            return False
        return self._add_offset_if_exists(node.children[i], key, offset)

    def insert(self, key, offset):
        """
        Chèn một khóa mới cùng offset tương ứng vào cây B-Tree.

        Args:
            key: Khóa cần chèn.
            offset (int): Địa chỉ vật lý của dữ liệu trên tệp nhị phân.
        """
        if self.root.keys and self._add_offset_if_exists(self.root, key, offset):
            return

        split_data = self._insert_non_full(self.root, key, offset)
        if split_data is not None:
            new_root = BTreeNode(leaf=False)
            new_root.keys = [split_data['key']]
            new_root.offsets = [split_data['offset']]
            new_root.children = [self.root, split_data['right_node']]
            self.root = new_root

    def _insert_non_full(self, node, key, offset):
        """
        Hàm hỗ trợ chèn đệ quy vào một nút chưa đầy.

        Args:
            node (BTreeNode): Nút hiện tại đang xét.
            key: Khóa cần chèn.
            offset (int): Địa chỉ vật lý.

        Returns:
            dict hoặc None: Trả về dữ liệu chia tách (nếu nút con bị đầy và chia tách thành công), ngược lại trả về None.
        """
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1

        if node.leaf:
            node.keys.insert(i, key)
            node.offsets.insert(i, [offset]) 
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
        """
        Tách một nút thành hai nút khi số lượng khóa vượt quá mức tối đa.

        Args:
            node (BTreeNode): Nút cần chia tách.

        Returns:
            dict: Chứa khóa trung vị (key), offset trung vị và nút mới bên phải (right_node) để đẩy lên nút cha.
        """
        mid_index = len(node.keys) >> 1
        mid_key = node.keys[mid_index]
        mid_offset = node.offsets[mid_index]

        right_node = BTreeNode(leaf=node.leaf)
        right_node.keys = node.keys[mid_index + 1:]
        right_node.offsets = node.offsets[mid_index + 1:]

        if not node.leaf:
            right_node.children = node.children[mid_index + 1:]
            node.children = node.children[:mid_index + 1]
        
        del node.keys[mid_index:]
        del node.offsets[mid_index:]

        return {
            'key': mid_key,
            'offset': mid_offset,
            'right_node': right_node
        }

    def delete(self, key, offset_to_remove=None):
        """
        Xóa một khóa khỏi cây B-Tree.

        Args:
            key: Khóa cần xóa.
            offset_to_remove (int, optional): Offset cụ thể cần xóa. Sử dụng trong trường hợp 
                                              một khóa có nhiều offset.

        Returns:
            bool: True nếu xóa thành công, False nếu ngược lại.
        """
        if not self.root.keys: 
            return False
        is_deleted = self._delete_recursive(self.root, key, offset_to_remove)
        if len(self.root.keys) == 0 and not self.root.leaf:
            self.root = self.root.children[0]
        return is_deleted

    def _delete_recursive(self, node, key, offset_to_remove):
        """
        Hàm hỗ trợ thực hiện xóa đệ quy một khóa và xử lý việc nối/chia nút.

        Args:
            node (BTreeNode): Nút hiện tại đang xét.
            key: Khóa cần xóa.
            offset_to_remove (int): Offset cụ thể cần xóa.

        Returns:
            bool: Trạng thái xóa thành công hay thất bại.
        """
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1

        if i < len(node.keys) and key == node.keys[i]:
            if offset_to_remove is not None and offset_to_remove in node.offsets[i]:
                node.offsets[i].remove(offset_to_remove)
                if len(node.offsets[i]) > 0:
                    return True 

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
                is_deleted = self._delete_recursive(node.children[i], pred_key, None)
        else:
            if node.leaf: 
                return False
            is_deleted = self._delete_recursive(node.children[i], key, offset_to_remove)

        if not node.leaf and len(node.children[i].keys) < self.min_keys:
            self._fix_underflow(node, i)

        return is_deleted
    
    def _get_max_node(self, node):
        """
        Tìm nút chứa giá trị khóa lớn nhất trong một nhánh cây.

        Args:
            node (BTreeNode): Nút gốc của nhánh cây cần tìm.

        Returns:
            BTreeNode: Nút chứa giá trị lớn nhất.
        """
        current = node
        while not current.leaf: 
            current = current.children[-1]
        return current
    
    def _fix_underflow(self, parent, index):
        """
        Xử lý tình trạng thiếu hụt khóa của một nút con bằng cách mượn khóa 
        từ nút anh em lân cận hoặc gộp hai nút lại với nhau.

        Args:
            parent (BTreeNode): Nút cha chứa nút bị thiếu hụt.
            index (int): Chỉ số của nút con bị thiếu hụt.
        """
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
        """
        Gộp một nút con với nút anh em bên phải của nó cùng với khóa trung gian từ nút cha.

        Args:
            parent (BTreeNode): Nút cha chứa hai nút con cần gộp.
            index (int): Chỉ số của nút con bên trái cần gộp.
        """
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
        """
        Truy xuất trạng thái phân cấp hiện tại của cây B-Tree.

        Returns:
            dict: Cấu trúc từ điển mô tả toàn bộ cây. Trả về từ điển rỗng nếu cây chưa có phần tử nào.
        """
        if not self.root.keys: 
            return {}
        return self.root.to_dict()