# 🌳 Hệ Thống Quản Lý Sinh Viên - B-Tree Indexing

> Mô phỏng ứng dụng cấu trúc dữ liệu B-Tree vào việc tối ưu hóa lập chỉ mục và thao tác trực tiếp trên Cơ sở dữ liệu tệp nhị phân.

## 🚀 Live Demo
🌐 **[Trải nghiệm trực tiếp dự án tại đây]([https://leafy-liger-fd5843.netlify.app/])**

*(Lưu ý: Hệ thống sử dụng Backend được host trên PythonAnywhere, có thể mất vài giây để khởi động trong lần truy cập đầu tiên).*

---

## ✨ Tính năng nổi bật

- **Lập chỉ mục kép (Dual B-Tree):** Tự động duy trì và cân bằng hai cây B-Tree song song để tìm kiếm siêu tốc theo **Mã Sinh Viên (ID)** và **Họ Tên (Name)**.
- **Trực quan hóa thời gian thực:** Tích hợp thư viện `D3.js` để tự động vẽ lại cây B-Tree mỗi khi có thao tác Thêm/Xóa. Hỗ trợ cuộn ngang và chống chồng chéo Node khi dữ liệu lớn.
- **Thao tác File Nhị Phân:** Không sử dụng các hệ quản trị CSDL có sẵn. Mọi thao tác đọc/ghi đều tác động trực tiếp lên byte của file `students.dat` thông qua cơ chế Offset.
---

## 🛠️ Công nghệ sử dụng

- **Frontend:** HTML5, CSS3, JavaScript (ES6+), thư viện vẽ đồ thị D3.js v7, SweetAlert2.
- **Backend:** Python 3, Flask, Flask-CORS.
- **Lưu trữ:** Binary File Storage (`students.dat`).
- **Tài liệu:** Báo cáo học thuật trình bày bằng LaTeX.

---

## 📁 Cấu trúc dự án

```text
StudentManagement_BTree/
│
├── backend/                   # Chứa logic xử lý API và Cấu trúc B-Tree
│   ├── app.py                 # File khởi chạy Server Flask
│   ├── b_tree.py              # Thuật toán cấu trúc cây đa phân
│   ├── storage.py             # Xử lý tệp nhị phân (Binary Storage)
│   └── requirements.txt       # Danh sách thư viện Python
│
├── frontend/                  # Giao diện người dùng
│   ├── index.html             # Trang chủ
│   ├── css
|   |   |── style.css              # File định dạng giao diện
│   └── js
|       |──main.js                # Xử lý logic hiển thị và gọi API
│
└── latex/                     # Mã nguồn báo cáo đồ án
    ├── main.tex               # File báo cáo chính (tổng hợp các phần)
    ├── setup.tex              # Cấu hình thư viện, lề giấy và định dạng
    ├── titlepage.tex          # Thiết kế trang bìa của báo cáo
    └── images/                # Hình ảnh minh họa cho báo cáo