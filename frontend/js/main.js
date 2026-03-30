const API_URL = "https://huyphong1344.pythonanywhere.com/api";
let currentTreeType = 'id';

document.addEventListener("DOMContentLoaded", () => {
    fetchStudents();
    renderTree('id');
});

async function fetchStudents() {
    try {
        const res = await fetch(`${API_URL}/students?_=${new Date().getTime()}`);
        const data = await res.json();
        
        const tbody = document.querySelector("#student-table tbody");
        tbody.innerHTML = ""; 
        
        const renderRow = (item) => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>${item.offset}</strong></td>
                <td>${item.data.student_id}</td>
                <td>${item.data.name}</td>
                <td>${item.data.gender}</td>
            `;
            tbody.appendChild(tr); 
        };

        if (data.length <= 10) {
            data.forEach(renderRow);
        } else {
            const top5 = data.slice(0, 5);
            const bottom5 = data.slice(data.length - 5);

            top5.forEach(renderRow);

            const trDots = document.createElement("tr"); 
            trDots.innerHTML = `
                <td colspan="4" style="text-align: center; font-weight: bold; color: #888; background-color: #f9f9f9;">
                    ... (${data.length - 10} sinh viên khác bị ẩn) ...
                </td>
            `;
            tbody.appendChild(trDots);

            bottom5.forEach(renderRow);
        }
    } catch (err) {
        console.error("Lỗi tải danh sách:", err);
    }
}

async function addStudent() {
    const id = document.getElementById('add-id').value;
    const name = document.getElementById('add-name').value;
    const gender = document.getElementById('add-gender').value;

    if(!id || !name) return alert("Vui lòng nhập đủ thông tin");

    const res = await fetch(`${API_URL}/students`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ student_id: id, name: name, gender: gender })
    });

    const result = await res.json();
    if (res.ok) {
        // Thông báo xịn có Tiêu đề, Nội dung và Icon
        Swal.fire({
            title: "Thêm thành công!",
            text: "Sinh viên đã được cập nhật vào cây B-Tree",
            icon: "success",
            timer: 2000,             // Tự động tắt sau 2 giây
            showConfirmButton: false // Ẩn nút OK cho mượt
        });

        document.getElementById('add-id').value = '';
        document.getElementById('add-name').value = '';
        document.getElementById('add-gender').value = '';
        
        await fetchStudents();
        await renderTree(currentTreeType);
    } else {
        Swal.fire({
            title: "Không thể thêm!",
            text: result.error,
            icon: "error",
            confirmButtonText: "Đã hiểu"
        });
    }
}

async function deleteStudent() {
    const id = document.getElementById('action-id').value;
    if(!id) return alert("Vui lòng nhập MSSV để xóa");

    const res = await fetch(`${API_URL}/students/${id}`, { method: 'DELETE' });
    const result = await res.json();
    
    if (res.ok) {
        Swal.fire({
            title: "Xóa thành công!",
            text: "Dữ liệu sinh viên đã được loại bỏ khỏi hệ thống B-Tree.",
            icon: "success",
            timer: 2000,             
            showConfirmButton: false
        });
        
        await fetchStudents();
        await renderTree(currentTreeType);
    } else {
        Swal.fire({
            title: "Xóa thất bại!",
            text: result.error,
            icon: "error",
            confirmButtonText: "Đã hiểu"
        });
    }
}

async function searchStudent() {
    const type = document.getElementById('search-type').value;
    const query = document.getElementById('action-id').value;
    if(!query) return alert("Vui lòng nhập từ khóa");
    
    const res = await fetch(`${API_URL}/search?type=${type}&query=${query}`);
    const resultP = document.getElementById('search-result');
    resultP.innerHTML = ""; 
    
    if(res.ok) {
        const results = await res.json();
        resultP.style.color = "green";
        results.forEach(item => {
            resultP.innerHTML += `<p>Tìm thấy: [Offset ${item.offset}] - ${item.student.student_id} - ${item.student.name}</p>`;
        });
    } else {
        const err = await res.json();
        resultP.style.color = "red";
        resultP.innerHTML = `<p>${err.error}</p>`;
    }
}

async function renderTree(treeType) {
    currentTreeType = treeType;
    document.getElementById("tree-title").innerText = `Cấu trúc Cây B-Tree (Đang xem: ${treeType.toUpperCase()})`;
    
    document.getElementById("btn-tree-id").className = treeType === 'id' ? "active-btn" : "";
    document.getElementById("btn-tree-name").className = treeType === 'name' ? "active-btn" : "";

    const res = await fetch(`${API_URL}/btree/${treeType}?_=${new Date().getTime()}`);
    const treeData = await res.json();

    const svg = d3.select("#btree-svg");
    svg.selectAll("*").remove();
    if (Object.keys(treeData).length === 0) return; 

    const root = d3.hierarchy(treeData);

    const treeLayout = d3.tree().nodeSize([250, 120]);
    treeLayout(root);

    let minX = 0, maxX = 0, maxY = 0;
    root.descendants().forEach(d => {
        if (d.x < minX) minX = d.x;
        if (d.x > maxX) maxX = d.x;
        if (d.y > maxY) maxY = d.y;
    });

    const dynamicWidth = maxX - minX + 400; 
    const dynamicHeight = maxY + 200;

    svg.attr("width", dynamicWidth)
       .attr("height", dynamicHeight);
    
    if (svg.node().parentNode) {
        svg.node().parentNode.style.overflowX = "auto";
        svg.node().parentNode.style.width = "100%";
    }

    const g = svg.append("g")
        .attr("transform", `translate(${-minX + 200}, 50)`);


    g.selectAll(".link")
        .data(root.links())
        .enter().append("path")
        .attr("class", "link")
        .attr("fill", "none")
        .attr("stroke", "#999")
        .attr("stroke-width", 2)
        .attr("d", d3.linkVertical().x(d => d.x).y(d => d.y));

    const node = g.selectAll(".node")
        .data(root.descendants())
        .enter().append("g")
        .attr("class", "node")
        .attr("transform", d => `translate(${d.x},${d.y})`);

    node.append("rect")
        .attr("width", d => {
            const textLen = d.data.name ? d.data.name.length : 0;
            return Math.max(100, textLen * 10 + 20); // Giãn rộng rect theo chữ
        })
        .attr("height", 35)
        .attr("x", d => {
            const textLen = d.data.name ? d.data.name.length : 0;
            return -Math.max(100, textLen * 10 + 20) / 2;
        })
        .attr("y", -17.5)
        .attr("fill", "#fff")
        .attr("stroke", "steelblue")
        .attr("stroke-width", 2)
        .attr("rx", 8);

    node.append("text")
        .attr("dy", 5)
        .attr("text-anchor", "middle")
        .style("font-family", "monospace")
        .style("font-weight", "bold")
        .text(d => d.data.name);
}