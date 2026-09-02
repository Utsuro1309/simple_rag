from pydantic import BaseModel
from typing import Optional

class DocumentChunk(BaseModel):
    content: str
    source_file: str
    doc_type: str
    page_number: Optional[int] = None
    token_count: Optional[int] = None