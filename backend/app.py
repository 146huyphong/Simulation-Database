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

# Yêu cầu đồ án: Cây bậc 3
btree_id = BTree(t=3)
btree_name = BTree(t=3)

def rebuild_indexes():
    """Nạp lại dữ liệu từ File Nhị Phân lên Cây B-Tree khi server khởi động"""
    print("🔄 Đang khôi phục dữ liệu từ ổ cứng...")
    active_records = storage.load_all_for_index()
    for record in active_records:
        offset = record['offset']
        student = record['student']
        btree_id.insert(student.student_id, offset)
        btree_name.insert(student.name, offset)
    print(f"✅ Đã tải xong {len(active_records)} sinh viên vào B-Tree!")

rebuild_indexes()

# ==========================================
# CÁC API ENDPOINTS
# ==========================================

@app.route('/api/students', methods=['GET'])
def get_all_students():
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

    # Kiểm tra trùng ID
    if btree_id.search(student_id) is not None:
        return jsonify({"error": "Mã sinh viên đã tồn tại"}), 409

    new_student = Student(student_id, name, gender)
    
    # 1. Ghi xuống File nhị phân và nhận về offset vật lý
    offset = storage.insert(new_student)
    
    # 2. Chèn vào B-Tree (Cây name tự động xử lý mảng nếu trùng tên)
    btree_id.insert(student_id, offset)
    btree_name.insert(name, offset)

    return jsonify({
        "message": "Sinh viên đã được thêm thành công", 
        "offset": offset,
        "student": new_student.to_dict()
    }), 201

@app.route('/api/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    # Lấy offset vật lý từ BTree ID (Trả về một list, ID là duy nhất nên lấy index [0])
    offsets = btree_id.search(student_id)
    
    if not offsets:
        return jsonify({"error": "Không tìm thấy sinh viên"}), 404
        
    offset = offsets[0]

    # Đọc trực tiếp dưới ổ cứng lên để lấy tên (chuẩn bị xóa cây Name)
    student = storage.read(offset)
    if not student or student.is_deleted:
        return jsonify({"error": "Sinh viên không tồn tại hoặc đã bị xóa"}), 404

    # 1. Xóa dưới ổ cứng
    storage.delete(offset)
    
    # 2. Xóa trên B-Tree RAM (Truyền cả offset để xóa đúng người nếu trùng tên)
    btree_id.delete(student_id, offset)
    btree_name.delete(student.name, offset)

    return jsonify({"message": f"Sinh viên {student.student_id} đã được xóa"}), 200

@app.route('/api/search', methods=['GET'])
def search_students():
    search_type = request.args.get('type') # 'id' hoặc 'name'
    query = request.args.get('query')

    if not query:
        return jsonify({"error": "Vui lòng cung cấp từ khóa tìm kiếm"}), 400
    
    offsets = []
    if search_type == 'id':
        res = btree_id.search(query)
        if res: offsets = res
    elif search_type == 'name':
        res = btree_name.search(query)
        if res: offsets = res
    else:
        return jsonify({"error": "Loại tìm kiếm không hợp lệ"}), 400

    # Nếu tìm thấy các offset, lấy dữ liệu từ đĩa
    results = []
    for off in offsets:
        student = storage.read(off)
        if student and not student.is_deleted:
            results.append({
                "offset": off,
                "student": student.to_dict()
            })
            
    if results:
        return jsonify(results), 200
    
    return jsonify({"error": "Không tìm thấy sinh viên hoặc đã bị xóa"}), 404

@app.route('/api/btree/<tree_type>', methods=['GET'])
def get_tree(tree_type):
    if tree_type == 'id':
        return jsonify(btree_id.get_tree_state()), 200
    elif tree_type == 'name':
        return jsonify(btree_name.get_tree_state()), 200
    
    return jsonify({"error": "Loại cây không hợp lệ"}), 400

if __name__ == '__main__':
    print("Đang chạy server http://127.0.0.1:5000")
    app.run(debug=True, port=5000)