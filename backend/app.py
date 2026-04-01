from flask import Flask, jsonify, request   
from flask_cors import CORS
from b_tree import BTree, Student
from storage import BinaryStorage

app = Flask(__name__)
CORS(app)

storage = BinaryStorage('students.dat')

btree_id = BTree(t=3)
btree_name = BTree(t=3)

def rebuild_indexes():
    """
    Khôi phục lại chỉ mục B-Tree từ tệp lưu trữ nhị phân khi khởi động máy chủ.

    Hàm này sẽ đọc toàn bộ các bản ghi chưa bị đánh dấu xóa từ 'students.dat'.
    Sau đó, nạp mã sinh viên, họ tên và địa chỉ vật lý tương ứng của 
    từng bản ghi vào hai cây B-Tree để phục vụ cho việc tìm kiếm tốc độ cao.
    """
    print("Đang khôi phục dữ liệu từ ổ cứng...")
    active_records = storage.load_all_for_index()
    for record in active_records:
        offset = record['offset']
        student = record['student']
        btree_id.insert(student.student_id, offset)
        btree_name.insert(student.name, offset)
    print(f"Đã tải xong {len(active_records)} sinh viên vào B-Tree!")

rebuild_indexes()

@app.route('/api/students', methods=['GET'])
def get_all_students():
    """
    Truy xuất danh sách toàn bộ sinh viên đang hoạt động.

    Returns:
        Response: Chuỗi JSON chứa danh sách các từ điển. Mỗi từ điển bao gồm 
                  địa chỉ vật lý (offset) và dữ liệu chi tiết của sinh viên.
                  Trạng thái HTTP 200 OK.
    """
    active_records = storage.load_all_for_index()
    result = [
        {"offset": r['offset'], "data": r['student'].to_dict()} 
        for r in active_records
    ]
    return jsonify(result), 200

@app.route('/api/students', methods=['POST'])
def add_student():
    """
    Thêm một sinh viên mới vào cơ sở dữ liệu và cập nhật chỉ mục B-Tree.

    Yêu cầu dữ liệu đầu vào (JSON) phải chứa 'student_id', 'name' và 'gender'.
    Hàm sẽ kiểm tra tính duy nhất của mã sinh viên. Nếu hợp lệ, dữ liệu sẽ được 
    ghi xuống tệp nhị phân, sau đó địa chỉ vật lý (offset) trả về sẽ được chèn 
    vào cả hai cây B-Tree (ID và Tên).

    Returns:
        Response: Chuỗi JSON thông báo thành công, kèm theo offset và dữ liệu 
                  sinh viên vừa tạo.
                  Trả về HTTP 400 nếu thiếu dữ liệu, hoặc HTTP 409 nếu trùng ID.
    """
    data = request.json
    student_id = data.get('student_id')
    name = data.get('name')
    gender = data.get('gender')

    if not student_id or not name or not gender:
        return jsonify({"error": "Thiếu thông tin sinh viên"}), 400

    if btree_id.search(student_id) is not None:
        return jsonify({"error": "Mã sinh viên đã tồn tại"}), 409

    new_student = Student(student_id, name, gender)
    
    offset = storage.insert(new_student)
    
    btree_id.insert(student_id, offset)
    btree_name.insert(name, offset)

    return jsonify({
        "message": "Sinh viên đã được thêm thành công", 
        "offset": offset,
        "student": new_student.to_dict()
    }), 201

@app.route('/api/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    """
    Đánh dấu xóa một sinh viên trong tệp nhị phân và gỡ bỏ khỏi chỉ mục B-Tree.

    Hàm sử dụng B-Tree ID để tìm nhanh địa chỉ vật lý của sinh viên.
    Sau khi xác thực dữ liệu trên ổ cứng, hàm sẽ tiến hành đánh dấu xóa bản ghi 
    và loại bỏ các node tương ứng trên cả hai cây B-Tree.

    Args:
        student_id (str): Mã số của sinh viên cần xóa.

    Returns:
        Response: Chuỗi JSON thông báo xóa thành công (HTTP 200 OK).
                  Trả về HTTP 404 nếu không tìm thấy sinh viên hoặc đã bị xóa trước đó.
    """
    offsets = btree_id.search(student_id)
    
    if not offsets:
        return jsonify({"error": "Không tìm thấy sinh viên"}), 404
        
    offset = offsets[0]

    student = storage.read(offset)
    if not student or student.is_deleted:
        return jsonify({"error": "Sinh viên không tồn tại hoặc đã bị xóa"}), 404

    storage.delete(offset)
    
    btree_id.delete(student_id, offset)
    btree_name.delete(student.name, offset)

    return jsonify({"message": f"Sinh viên {student.student_id} đã được xóa"}), 200

@app.route('/api/search', methods=['GET'])
def search_students():
    """
    Tìm kiếm thông tin sinh viên dựa trên tiêu chí được chỉ định.

    Hàm nhận tham số 'type' và 'query' từ URL.
    Sử dụng cây B-Tree tương ứng để lấy danh sách các offsets, 
    sau đó truy xuất trực tiếp dữ liệu chi tiết từ tệp nhị phân để trả về.

    Returns:
        Response: Chuỗi JSON chứa danh sách các sinh viên khớp với từ khóa 
                  và trạng thái HTTP 200 OK.
                  Trả về HTTP 400 nếu sai tham số, HTTP 404 nếu không có kết quả.
    """
    search_type = request.args.get('type') 
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
    """
    Truy xuất cấu trúc hiện tại của cây B-Tree để phục vụ cho việc vẽ biểu đồ.

    Args:
        tree_type (str): Loại cây cần lấy dữ liệu ('id' hoặc 'name').

    Returns:
        Response: Chuỗi JSON chứa cấu trúc phân cấp của cây B-Tree (HTTP 200 OK).
                  Trả về HTTP 400 nếu loại cây yêu cầu không tồn tại.
    """
    if tree_type == 'id':
        return jsonify(btree_id.get_tree_state()), 200
    elif tree_type == 'name':
        return jsonify(btree_name.get_tree_state()), 200
    
    return jsonify({"error": "Loại cây không hợp lệ"}), 400

if __name__ == '__main__':
    print("Đang chạy server http://127.0.0.1:5000")
    app.run(debug=True, port=5000)