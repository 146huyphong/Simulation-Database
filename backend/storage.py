import struct
import os
from b_tree import Student

class BinaryStorage:
    def __init__(self, filename='students.dat'):
        self.filename = filename
        self.format = '10s 50s 10s ?'
        self.record_size = struct.calcsize(self.format)
        
        if not os.path.exists(self.filename):
            open(self.filename, 'wb').close()

    def _pack_string(self, text, length):
        encoded = text.encode('utf-8')
        return encoded[:length].ljust(length, b'\0')

    def _unpack_string(self, byte_data):
        return byte_data.decode('utf-8').rstrip('\x00')

    def insert(self, student):
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
        with open(self.filename, 'rb') as f:
            f.seek(offset)
            data = f.read(self.record_size)
            if not data or len(data) < self.record_size: return None
                
            unpacked = struct.unpack(self.format, data)
            sid = self._unpack_string(unpacked[0])
            name = self._unpack_string(unpacked[1])
            gender = self._unpack_string(unpacked[2])
            is_deleted = unpacked[3]
            
            student = Student(sid, name, gender)
            student.is_deleted = is_deleted
            return student

    def delete(self, offset):
        student = self.read(offset)
        if student:
            with open(self.filename, 'r+b') as f:
                f.seek(offset)
                data = struct.pack(
                    self.format,
                    self._pack_string(student.student_id, 10),
                    self._pack_string(student.name, 50),
                    self._pack_string(student.gender, 10),
                )
                f.write(data)

    def load_all_for_index(self):
        students = []
        with open(self.filename, 'rb') as f:
            while True:
                offset = f.tell()
                data = f.read(self.record_size)
                if not data or len(data) < self.record_size: break
                    
                unpacked = struct.unpack(self.format, data)
                if not unpacked[3]: 
                    sid = self._unpack_string(unpacked[0])
                    name = self._unpack_string(unpacked[1])
                    gender = self._unpack_string(unpacked[2])
                    student = Student(sid, name, gender)
                    students.append({"offset": offset, "student": student})
        return students