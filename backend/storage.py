import struct
import os
from b_tree import Student

class BinaryStorage:
    def __init__(self, filename='students.dat'):
        self.filename = filename
        
        # Định dạng struct: 10s (chuỗi 10 byte), 50s (chuỗi 50 byte), 10s (chuỗi 10 byte), ? (1 byte boolean)
        self.format = '10s 50s 10s ?'
        self.record_size = struct.calcsize(self.format) # Sẽ tính ra 71 bytes
        
        # Tạo file mới nếu chưa tồn tại
        if not os.path.exists(self.filename):
            open(self.filename, 'wb').close()

    def _pack_string(self, text, length):
        """Mã hóa chuỗi thành byte UTF-8 và chèn thêm byte 0 (\x00) cho đủ độ dài"""
        encoded = text.encode('utf-8')
        # Cắt bớt nếu dài hơn quy định, sau đó lấp đầy bằng byte \x00
        return encoded[:length].ljust(length, b'\0')

    def _unpack_string(self, byte_data):
        """Giải mã byte thành chuỗi và loại bỏ các byte \x00 dư thừa"""
        return byte_data.decode('utf-8').rstrip('\x00')

    def insert(self, student):
        """Ghi sinh viên vào cuối file và trả về Offset (địa chỉ byte)"""
        with open(self.filename, 'ab') as f:
            offset = f.tell() # Lấy vị trí byte cuối cùng hiện tại
            
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
        """Nhảy đến địa chỉ offset và đọc đúng 71 bytes để khôi phục sinh viên"""
        with open(self.filename, 'rb') as f:
            f.seek(offset)
            data = f.read(self.record_size)
            
            if not data or len(data) < self.record_size:
                return None
                
            unpacked = struct.unpack(self.format, data)
            
            # Khôi phục lại đối tượng Student
            sid = self._unpack_string(unpacked[0])
            name = self._unpack_string(unpacked[1])
            gender = self._unpack_string(unpacked[2])
            is_deleted = unpacked[3]
            
            student = Student(sid, name, gender)
            student.is_deleted = is_deleted
            return student

    def delete(self, offset):
        """Đánh dấu xóa mềm (Tombstone) bằng cách ghi đè byte is_deleted"""
        student = self.read(offset)
        if student:
            student.is_deleted = True
            with open(self.filename, 'r+b') as f: # Mở chế độ đọc/ghi đè (r+b)
                f.seek(offset)
                data = struct.pack(
                    self.format,
                    self._pack_string(student.student_id, 10),
                    self._pack_string(student.name, 50),
                    self._pack_string(student.gender, 10),
                    student.is_deleted # Đã thành True
                )
                f.write(data)

    def load_all_for_index(self):
        """Duyệt toàn bộ file nhị phân để lấy danh sách và phục hồi B-Tree khi khởi động lại Server"""
        students = []
        with open(self.filename, 'rb') as f:
            while True:
                offset = f.tell()
                data = f.read(self.record_size)
                if not data or len(data) < self.record_size:
                    break
                    
                unpacked = struct.unpack(self.format, data)
                if not unpacked[3]: # Nếu is_deleted == False
                    sid = self._unpack_string(unpacked[0])
                    name = self._unpack_string(unpacked[1])
                    gender = self._unpack_string(unpacked[2])
                    
                    student = Student(sid, name, gender)
                    students.append({"offset": offset, "student": student})
                    
        return students