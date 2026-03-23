from flask import Flask, jsonify, request   
from flask_cors import CORS
from b_tree import BTree, Student
from storage import BinaryStorage

app = Flask(__name__)
CORS(app)

# ==========================================
# KHỞI TẠO STORAGE VÀ CHỈ MỤC B-TREE
# ==========================================
storage = BinaryStorage('students.dat')

btree_id = BTree(t=3)
btree_name = BTree(t=3)

def rebuild_indexes():
    """Hàm này chạy lúc server khởi động để nạp lại dữ liệu từ File Nhị Phân lên Cây B-Tree"""
    print("🔄 Đang khôi phục dữ liệu từ ổ cứng...")
    active_records = storage.load_all_for_index()
    for record in active_records:
        offset = record['offset']
        student = record['student']
        btree_id.insert(student.student_id, offset)
        btree_name.insert(student.name, offset)
    print(f"✅ Đã tải xong {len(active_records)} sinh viên vào B-Tree!")

# Chạy hàm khôi phục ngay khi app.py được thực thi
rebuild_indexes()

# ==========================================
# CÁC API ENDPOINTS
# ==========================================

@app.route('/api/students', methods=['GET'])
def get_all_students():
    # Load lại từ file nhị phân
    active_records = storage.load_all_for_index()
    result = [
        {"offset": r['offset'], "data": r['student'].to_dict()} 
        for r in active_records
    ]
    return jsonify(result), 200

@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.json
    student_id = data.get('student_id')
    name = data.get('name')
    gender = data.get('gender')

    if not student_id or not name or not gender:
        return jsonify({"error": "Thiếu thông tin sinh viên"}), 400

    if btree_id.search(student_id) is not None:
        return jsonify({"error": "Mã sinh viên đã tồn tại"}), 409

    new_student = Student(student_id, name, gender)
    
    # 1. Ghi xuống File nhị phân và nhận về offset vật lý
    offset = storage.insert(new_student)
    
    # 2. Chèn offset vật lý vào B-Tree
    btree_id.insert(student_id, offset)
    btree_name.insert(name, offset)

    return jsonify({
        "message": "Sinh viên đã được thêm thành công", 
        "offset": offset,
        "student": new_student.to_dict()
    }), 201

@app.route('/api/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    # Lấy offset vật lý từ BTree
    offset = btree_id.search(student_id)
    
    if offset is None:
        return jsonify({"error": "Không tìm thấy sinh viên"}), 404

    # Dùng offset để đọc trực tiếp dưới ổ cứng lên để lấy tên (chuẩn bị xóa cây Name)
    student = storage.read(offset)
    if not student or student.is_deleted:
        return jsonify({"error": "Sinh viên không tồn tại hoặc đã bị xóa"}), 404

    # Xóa dưới ổ cứng (cập nhật byte)
    storage.delete(offset)
    
    # Xóa trên B-Tree RAM
    btree_id.delete(student_id)
    btree_name.delete(student.name)

    return jsonify({"message": f"Sinh viên {student.student_id} - {student.name} đã được xóa thành công"}), 200

@app.route('/api/search', methods=['GET'])
def search_students():
    search_type = request.args.get('type')
    query = request.args.get('query')

    if not query:
        return jsonify({"error": "Vui lòng cung cấp từ khóa tìm kiếm"}), 400
    
    offset = None 
    if search_type == 'id':
        offset = btree_id.search(query)
    elif search_type == 'name':
        offset = btree_name.search(query)
    else:
        return jsonify({"error": "Loại tìm kiếm không hợp lệ. Vui lòng sử dụng 'id' hoặc 'name'"}), 400

    # Lấy thông tin từ file nhị phân nếu tìm thấy offset
    if offset is not None:
        student = storage.read(offset)
        if student and not student.is_deleted:
            return jsonify({
                "offset": offset,
                "student": student.to_dict()
            }), 200
    
    return jsonify({"error": "Không tìm thấy sinh viên hoặc sinh viên đã bị xóa"}), 404

@app.route('/api/btree/<tree_type>', methods=['GET'])
def get_tree(tree_type):
    # Sử dụng root.to_dict() hoặc hàm get_tree_state() nếu bạn đã định nghĩa
    if tree_type == 'id':
        # Tránh lỗi nếu cây rỗng hoàn toàn
        if not btree_id.root.keys: return jsonify({}), 200
        return jsonify(btree_id.root.to_dict()), 200
    elif tree_type == 'name':
        if not btree_name.root.keys: return jsonify({}), 200
        return jsonify(btree_name.root.to_dict()), 200
    
    return jsonify({"error": "Loại cây không hợp lệ. Vui lòng sử dụng 'id' hoặc 'name'"}), 400

if __name__ == '__main__':
    print("Đang chạy server http://127.0.0.1:5000")
    app.run(debug=True, port=5000)