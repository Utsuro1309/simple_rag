from pydantic import BaseModel
from typing import Optional, List

class QueryRequest(BaseModel):
    question: str
    method: str  # "rag" hoặc "page_index"
    large_doc_name: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    sources: Optional[List[str]] = None
    pages: Optional[List[int]] = None