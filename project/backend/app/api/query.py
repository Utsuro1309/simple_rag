from fastapi import APIRouter, HTTPException
from app.models.schemas import QueryRequest, QueryResponse
from app.services.rag_service import query_rag_advanced
from app.services.page_index_service import page_index_manager

router = APIRouter(prefix="/query", tags=["query"])

@router.post("/", response_model=QueryResponse)
async def query(req: QueryRequest):
    if req.method == "rag":
        res = await query_rag_advanced(req.question)
        return QueryResponse(answer=res["answer"], sources=res.get("sources"))
    elif req.method == "page_index":
        if not req.large_doc_name:
            raise HTTPException(400, "large_doc_name required")
        res = await page_index_manager.query_page_index(req.question, req.large_doc_name)
        return QueryResponse(answer=res["answer"], pages=res.get("pages"))
    else:
        raise HTTPException(400, "method must be 'rag' or 'page_index'")