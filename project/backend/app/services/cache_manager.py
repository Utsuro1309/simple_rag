import hashlib
import logging

logger = logging.getLogger(__name__)

class RAGCacheManager:
    def __init__(self):
        self.query_cache = {}
    
    def _key(self, query: str, method: str) -> str:
        return hashlib.md5(f"{query}|{method}".encode()).hexdigest()
    
    def get_from_query_cache(self, query: str, method: str):
        return self.query_cache.get(self._key(query, method))
    
    def set_query_cache(self, query: str, method: str, answer: dict):
        self.query_cache[self._key(query, method)] = answer
    
    def invalidate_for_document(self, filename: str):
        to_delete = [k for k, v in self.query_cache.items() if "sources" in v and filename in v["sources"]]
        for k in to_delete:
            del self.query_cache[k]
        logger.info(f"Invalidated {len(to_delete)} entries for {filename}")

cache_manager = RAGCacheManager()