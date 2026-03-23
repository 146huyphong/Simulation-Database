from flask import Flask, jsonify, request   
from flask_cors import CORS
from b_tree import BTree, Student

app = Flask(__name__)

CORS(app)

students_db = []

btree_id = BTree(t=3)
btree_name = BTree(t=3)

@app.route('/api/students', methods=['GET'])
def get_all_students():
    active_students = [
        {"offset": i, "data": student.to_dict()}
        for i, student in enumerate(students_db)
        if not student.is_deleted
    ]

    return jsonify(active_students), 200

@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.json
    student_id = data.get('student_id')
    name = data.get('name')
    gender = data.get('gender')

    if not student_id or not name or not gender:
        return jsonify({"Lỗi": "Thiếu thông tin sinh viên"}), 400

    if btree_id.search(student_id) is not None:
        return jsonify({"Lỗi": "Mã sinh viên đã tồn tại"}), 409
    
    new_student = Student(student_id, name, gender)
    students_db.append(new_student)

    offset = len(students_db) - 1

    btree_id.insert(student_id, offset)
    btree_name.insert(name, offset)

    return jsonify({
        "message": "Sinh viên đã được thêm thành công",
        "offset": offset,
        "student": new_student.to_dict()
    }), 201

@app.route('/api/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    offset = btre_id.search(student_id)

    if offset is None or students_db[offset].is_deleted:
        return jsonify({"Lỗi": "Không tìm thấy sinh viên hoặc sinh viên đã bị xóa"}), 404
    
    name_to_delete = students_db[offset].name

    students_db[offset].is_deleted = True
    btree_id.delete(student_id)
    btree_name.delete(name_to_delete)

    return jsonify({"message": f"Sinh viên {students_db[offset].student_id} - {students_db[offset].name} đã được xóa thành công"}), 200

@app.route('/api/search', methods=['GET'])
def search_students():
    search_type = request.args.get('type')
    query = request.args.get('query')

    if not query:
        return jsonify({"Lỗi": "Vui lòng cung cấp từ khóa tìm kiếm"}), 400
    
    offset = None 

    if search_type == 'id':
        offset = btree_id.search(query)
    elif search_type == 'name':
        offset = btree_name.search(query)
    else:
        return jsonify({"Lỗi": "Loại tìm kiếm không hợp lệ. Vui lòng sử dụng 'id' hoặc 'name'"}), 400

    if offset is not None and not students_db[offset].is_deleted:
        return jsonify({
            "offset": offset,
            "student": students_db[offset].to_dict()
        }), 200
    
    return jsonify({"Lỗi": "Không tìm thấy sinh viên hoặc sinh viên đã bị xóa"}), 404

@app.route('/api/btree/<tree_type>', methods=['GET'])
def get_tree(tree_type):
    if tree_type == 'id':
        return jsonify(btree_id.root.to_dict()), 200
    elif tree_type == 'name':
        return jsonify(btree_name.root.to_dict()), 200
    
    return jsonify({"Lỗi": "Loại cây không hợp lệ. Vui lòng sử dụng 'id' hoặc 'name'"}), 400

if __name__ == '__main__':
    print("Đang chạy server Flask trên http://127.0.0.1:5000")
    app.run(debug=True,port=5000)