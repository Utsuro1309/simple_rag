from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.file_processor import process_small_document, process_large_document_by_page
from app.services.weaviate_client import client
from app.services.page_index_service import page_index_manager

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/small")
async def upload_small(files: list[UploadFile] = File(...)):
    all_chunks = []
    for file in files:
        content = await file.read()
        chunks = process_small_document(content, file.filename)
        all_chunks.extend(chunks)
    
    for chunk in all_chunks:
        client.data_object.create(
            data_object={
                "content": chunk["content"],
                "source_file": chunk["source_file"],
                "doc_type": "small"
            },
            class_name="Document"
        )
    return {"message": f"Uploaded {len(files)} files, indexed {len(all_chunks)} chunks"}

@router.post("/large")
async def upload_large(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Only PDF allowed for large document")
    content = await file.read()
    await page_index_manager.add_large_document(content, file.filename)
    
    # Cũng lưu các trang vào Weaviate để hybrid search
    pages = process_large_document_by_page(content, file.filename)
    for page in pages:
        client.data_object.create(
            data_object={
                "content": page["content"],
                "source_file": page["source_file"],
                "doc_type": "large",
                "page_number": page["page_number"]
            },
            class_name="Document"
        )
    return {"message": f"Uploaded {file.filename} with {len(pages)} pages"}