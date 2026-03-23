const API_URL = "http://127.0.0.1:5000/api";

// Hàm chạy ngay khi web load xong
document.addEventListener("DOMContentLoaded", () => {
    fetchStudents();
    renderTree();
});

// ==========================================
// 1. CÁC HÀM GIAO TIẾP API (CRUD)
// ==========================================

async function fetchStudents() {
    const res = await fetch(`${API_URL}/students`);
    const data = await res.json();
    
    const tbody = document.querySelector("#student-table tbody");
    tbody.innerHTML = ""; // Xóa dữ liệu cũ
    
    data.forEach(item => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><strong>${item.offset}</strong></td>
            <td>${item.data.student_id}</td>
            <td>${item.data.name}</td>
            <td>${item.data.gender}</td>
        `;
        tbody.appendChild(tr);
    });
}

async function addStudent() {
    const id = document.getElementById('add-id').value;
    const name = document.getElementById('add-name').value;
    const gender = document.getElementById('add-gender').value;

    const res = await fetch(`${API_URL}/students`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ student_id: id, name: name, gender: gender })
    });

    const result = await res.json();
    if(res.ok) {
        alert("Thêm thành công!");
        fetchStudents();
        renderTree();
    } else {
        alert("Lỗi: " + result.error);
    }
}

async function deleteStudent() {
    const id = document.getElementById('action-id').value;
    const res = await fetch(`${API_URL}/students/${id}`, { method: 'DELETE' });
    
    const result = await res.json();
    if(res.ok) {
        alert("Xóa thành công!");
        fetchStudents();
        renderTree();
    } else {
        alert("Lỗi: " + result.error);
    }
}

async function searchStudent() {
    const query = document.getElementById('action-id').value;
    // Tạm thời mặc định tìm theo ID để minh họa
    const res = await fetch(`${API_URL}/search?type=id&query=${query}`);
    
    const result = await res.json();
    const resultP = document.getElementById('search-result');
    
    if(res.ok) {
        resultP.innerText = `Tìm thấy! Offset: ${result.offset} - Tên: ${result.student.name}`;
    } else {
        resultP.innerText = result.error;
    }
}

// ==========================================
// 2. HÀM VẼ CÂY B-TREE BẰNG D3.JS
// ==========================================

async function renderTree() {
    const res = await fetch(`${API_URL}/btree/id`);
    const treeData = await res.json();

    // Xóa cây cũ nếu có
    d3.select("#btree-svg").selectAll("*").remove();

    if (Object.keys(treeData).length === 0) return; // Cây rỗng

    const svg = d3.select("#btree-svg");
    const width = svg.node().getBoundingClientRect().width;
    const height = 500;
    const margin = {top: 40, right: 20, bottom: 40, left: 20};

    const g = svg.append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // Thiết lập D3 Tree Layout
    const treeLayout = d3.tree().size([width - margin.left - margin.right, height - 100]);
    const root = d3.hierarchy(treeData);
    
    treeLayout(root);

    // Vẽ các đường nối (Links)
    g.selectAll(".link")
        .data(root.links())
        .enter().append("path")
        .attr("class", "link")
        .attr("d", d3.linkVertical()
            .x(d => d.x)
            .y(d => d.y)
        );

    // Vẽ các Nút (Nodes)
    const node = g.selectAll(".node")
        .data(root.descendants())
        .enter().append("g")
        .attr("class", "node")
        .attr("transform", d => `translate(${d.x},${d.y})`);

    // Vẽ hình chữ nhật bao quanh Node
    node.append("rect")
        .attr("width", 80)
        .attr("height", 30)
        .attr("x", -40) // Căn giữa chữ nhật theo tọa độ x
        .attr("y", -15);

    // Hiển thị Khóa bên trong Node (Trường 'name' được tạo từ to_dict())
    node.append("text")
        .attr("dy", 5)
        .text(d => d.data.name);
}