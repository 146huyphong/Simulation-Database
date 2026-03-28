const API_URL = "http://127.0.0.1:5000/api";
let currentTreeType = 'id';

document.addEventListener("DOMContentLoaded", () => {
    fetchStudents();
    renderTree('id');
});

async function fetchStudents() {
    const res = await fetch(`${API_URL}/students?_=${new Date().getTime()}`);
    const data = await res.json();
    
    const tbody = document.querySelector("#student-table tbody");
    tbody.innerHTML = ""; 
    
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
        document.getElementById('add-id').value = '';
        document.getElementById('add-name').value = '';
        document.getElementById('add-gender').value = '';
        
        // Thêm chữ await vào đây để chờ tải xong mới kết thúc
        await fetchStudents();
        await renderTree(currentTreeType);
    } else {
        alert("Lỗi: " + result.error);
    }
}

async function deleteStudent() {
    // Luôn xóa bằng ID cho chính xác
    const id = document.getElementById('action-id').value;
    const res = await fetch(`${API_URL}/students/${id}`, { method: 'DELETE' });
    
    const result = await res.json();
    if(res.ok) {
        alert("Xóa thành công!");
        fetchStudents();
        renderTree(currentTreeType);
    } else {
        alert("Lỗi: " + result.error);
    }
}

async function searchStudent() {
    const type = document.getElementById('search-type').value;
    const query = document.getElementById('action-id').value;
    
    const res = await fetch(`${API_URL}/search?type=${type}&query=${query}`);
    const resultP = document.getElementById('search-result');
    resultP.innerHTML = ""; 
    
    if(res.ok) {
        const results = await res.json();
        resultP.style.color = "green";
        results.forEach(item => {
            resultP.innerHTML += `<p>✅ Tìm thấy: [Offset ${item.offset}] - ${item.student.student_id} - ${item.student.name}</p>`;
        });
    } else {
        const err = await res.json();
        resultP.style.color = "red";
        resultP.innerHTML = `<p>❌ ${err.error}</p>`;
    }
}

// ==========================================
// HÀM VẼ CÂY B-TREE BẰNG D3.JS
// ==========================================

async function renderTree(treeType) {
    currentTreeType = treeType;
    document.getElementById("tree-title").innerText = `Cấu trúc Cây B-Tree (Đang xem: ${treeType.toUpperCase()})`;
    
    document.getElementById("btn-tree-id").className = treeType === 'id' ? "active-btn" : "";
    document.getElementById("btn-tree-name").className = treeType === 'name' ? "active-btn" : "";

    // Thêm timestamp để ép vẽ lại cây B-Tree mới nhất
    const res = await fetch(`${API_URL}/btree/${treeType}?_=${new Date().getTime()}`);
    const treeData = await res.json();

    d3.select("#btree-svg").selectAll("*").remove();
    if (Object.keys(treeData).length === 0) return; 

    // ... (Toàn bộ phần vẽ D3.js phía dưới bạn GIỮ NGUYÊN)
    const svg = d3.select("#btree-svg");
    const width = svg.node().getBoundingClientRect().width || 800;
    const height = 500;
    const margin = {top: 40, right: 20, bottom: 40, left: 20};

    const g = svg.append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const treeLayout = d3.tree().size([width - margin.left - margin.right, height - 100]);
    const root = d3.hierarchy(treeData);
    treeLayout(root);

    g.selectAll(".link")
        .data(root.links())
        .enter().append("path")
        .attr("class", "link")
        .attr("fill", "none")
        .attr("stroke", "#ccc")
        .attr("stroke-width", 2)
        .attr("d", d3.linkVertical().x(d => d.x).y(d => d.y));

    const node = g.selectAll(".node")
        .data(root.descendants())
        .enter().append("g")
        .attr("class", "node")
        .attr("transform", d => `translate(${d.x},${d.y})`);

    node.append("rect")
        .attr("width", d => Math.max(80, d.data.name.length * 8 + 20))
        .attr("height", 30)
        .attr("x", d => -Math.max(80, d.data.name.length * 8 + 20) / 2)
        .attr("y", -15)
        .attr("fill", "white")
        .attr("stroke", "steelblue")
        .attr("stroke-width", 2)
        .attr("rx", 5);

    node.append("text")
        .attr("dy", 5)
        .attr("text-anchor", "middle")
        .text(d => d.data.name);
}