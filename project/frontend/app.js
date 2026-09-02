const API_BASE = "http://localhost:8000";

document.getElementById("methodSelect").addEventListener("change", function() {
    const advice = document.getElementById("advice");
    const largeInput = document.getElementById("largeDocName");
    if (this.value === "rag") {
        advice.innerHTML = "💡 Lời khuyên: Dùng RAG cho nhiều tài liệu nhỏ, không cần trích dẫn chính xác trang. Hệ thống dùng hybrid search + reranking.";
        largeInput.style.display = "none";
    } else {
        advice.innerHTML = "💡 Lời khuyên: Dùng Page Index cho tài liệu lớn có cấu trúc (báo cáo tài chính, 10-K). Trả về số trang chính xác.";
        largeInput.style.display = "block";
    }
});

document.getElementById("uploadSmall").onclick = async () => {
    const files = document.getElementById("smallFiles").files;
    if (!files.length) return alert("Chọn file");
    const formData = new FormData();
    for (let f of files) formData.append("files", f);
    const res = await fetch(`${API_BASE}/upload/small`, { method: "POST", body: formData });
    const data = await res.json();
    alert(data.message || "Upload thành công");
};

document.getElementById("uploadLarge").onclick = async () => {
    const file = document.getElementById("largeFile").files[0];
    if (!file) return alert("Chọn file PDF");
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE}/upload/large`, { method: "POST", body: formData });
    const data = await res.json();
    alert(data.message || "Upload thành công");
};

document.getElementById("askBtn").onclick = async () => {
    const method = document.getElementById("methodSelect").value;
    const question = document.getElementById("question").value;
    if (!question) return alert("Nhập câu hỏi");
    const body = { question, method };
    if (method === "page_index") {
        const docName = document.getElementById("largeDocName").value.trim();
        if (!docName) return alert("Nhập tên tài liệu lớn");
        body.large_doc_name = docName;
    }
    const res = await fetch(`${API_BASE}/query/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    });
    const data = await res.json();
    document.getElementById("answer").innerHTML = `<strong>Trả lời:</strong><br>${data.answer}`;
};