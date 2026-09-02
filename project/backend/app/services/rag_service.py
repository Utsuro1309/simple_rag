from app.services.hybrid_retriever import hybrid_search
from app.services.reranker import CrossEncoderReranker
from app.services.context_assembler import assemble_context
from app.services.llm_service import generate_answer
from app.services.cache_manager import cache_manager
import logging

logger = logging.getLogger(__name__)
reranker = CrossEncoderReranker()

async def query_rag_advanced(question: str, top_k: int = 10, rerank_top: int = 5) -> dict:
    # Cache check
    cached = cache_manager.get_from_query_cache(question, "rag")
    if cached:
        return cached
    
    raw_chunks = await hybrid_search(question, top_k=top_k)
    if not raw_chunks:
        return {"answer": "No relevant information found.", "sources": []}
    
    # Chuyển đổi định dạng từ dict của Weaviate
    docs_for_rerank = [{
        "content": obj["content"],
        "source_file": obj["source_file"],
        "page_number": obj.get("page_number", 0)
    } for obj in raw_chunks]
    
    reranked_docs = reranker.rerank(question, docs_for_rerank)
    top_chunks = reranked_docs[:rerank_top]
    
    context = assemble_context(top_chunks, max_tokens=3500)
    answer = await generate_answer(question, context)
    sources = list(set([chunk["source_file"] for chunk in top_chunks]))
    
    result = {"answer": answer, "sources": sources}
    cache_manager.set_query_cache(question, "rag", result)
    return result