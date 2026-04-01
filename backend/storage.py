import struct
import os
from b_tree import Student

class BinaryStorage:
    """
    Lớp cung cấp các phương thức thao tác đọc/ghi trực tiếp lên tệp nhị phân.
    Sử dụng thư viện struct để mã hóa và giải mã dữ liệu thành các byte cố định.
    """
    def __init__(self, filename='students.dat'):
        """
        Khởi tạo trình quản lý lưu trữ nhị phân.

        Args:
            filename (str): Tên tệp nhị phân dùng để lưu trữ dữ liệu. Mặc định là 'students.dat'.
        """
        self.filename = filename
        self.format = '10s 50s 10s ?'
        self.record_size = struct.calcsize(self.format)
        
        if not os.path.exists(self.filename):
            open(self.filename, 'wb').close()

    def _pack_string(self, text, length):
        """
        Mã hóa chuỗi văn bản thành mảng byte và căn lề cho đúng kích thước cố định.

        Args:
            text (str): Chuỗi văn bản cần mã hóa.
            length (int): Số byte tối đa và cố định của chuỗi.

        Returns:
            bytes: Mảng byte đã được đệm thêm ký tự rỗng cho đủ chiều dài.
        """
        encoded = text.encode('utf-8')
        return encoded[:length].ljust(length, b'\0')

    def _unpack_string(self, byte_data):
        """
        Giải mã mảng byte thành chuỗi văn bản và loại bỏ các ký tự rỗng thừa.

        Args:
            byte_data (bytes): Dữ liệu byte cần giải mã.

        Returns:
            str: Chuỗi văn bản hoàn chỉnh.
        """
        return byte_data.decode('utf-8').rstrip('\x00')

    def insert(self, student):
        """
        Ghi một bản ghi sinh viên mới vào cuối tệp nhị phân.

        Args:
            student (Student): Đối tượng Sinh viên cần lưu trữ.

        Returns:
            int: Địa chỉ vật lý (offset) tính bằng byte của bản ghi vừa chèn trong tệp.
        """
        with open(self.filename, 'ab') as f:
            offset = f.tell()
            data = struct.pack(
                self.format,
                self._pack_string(student.student_id, 10),
                self._pack_string(student.name, 50),
                self._pack_string(student.gender, 10),
                student.is_deleted
            )
            f.write(data)
            return offset

    def read(self, offset):
        """
        Đọc và giải mã dữ liệu của một sinh viên từ một địa chỉ vật lý cụ thể.

        Args:
            offset (int): Vị trí byte bắt đầu của bản ghi trong tệp.

        Returns:
            Student hoặc None: Trả về đối tượng Sinh viên nếu đọc thành công, trả về None nếu lỗi.
        """
        with open(self.filename, 'rb') as f:
            f.seek(offset)
            data = f.read(self.record_size)
            if not data or len(data) < self.record_size: 
                return None
                
            unpacked = struct.unpack(self.format, data)
            sid = self._unpack_string(unpacked[0])
            name = self._unpack_string(unpacked[1])
            gender = self._unpack_string(unpacked[2])
            is_deleted = unpacked[3]
            
            student = Student(sid, name, gender)
            student.is_deleted = is_deleted
            return student

    def delete(self, offset):
        """
        Đánh dấu xóa một bản ghi sinh viên tại địa chỉ vật lý được chỉ định.
        Hàm này không xóa hẳn dữ liệu khỏi ổ cứng mà chỉ cập nhật cờ is_deleted thành True.

        Args:
            offset (int): offset của bản ghi cần xóa.
        """
        student = self.read(offset)
        if student:
            with open(self.filename, 'r+b') as f:
                f.seek(offset)
                data = struct.pack(
                    self.format,
                    self._pack_string(student.student_id, 10),
                    self._pack_string(student.name, 50),
                    self._pack_string(student.gender, 10),
                    True  
                )
                f.write(data)

    def load_all_for_index(self):
        """
        Quét toàn bộ tệp nhị phân để tải các bản ghi đang hoạt động.
        Thường được gọi khi khởi động máy chủ để xây dựng lại chỉ mục B-Tree trên RAM.

        Returns:
            list: Danh sách chứa các từ điển, mỗi từ điển gồm 'offset' và đối tượng 'student'.
        """
        students = []
        with open(self.filename, 'rb') as f:
            while True:
                offset = f.tell()
                data = f.read(self.record_size)
                if not data or len(data) < self.record_size: 
                    break
                    
                unpacked = struct.unpack(self.format, data)
                if not unpacked[3]: 
                    sid = self._unpack_string(unpacked[0])
                    name = self._unpack_string(unpacked[1])
                    gender = self._unpack_string(unpacked[2])
                    student = Student(sid, name, gender)
                    students.append({"offset": offset, "student": student})
        return students