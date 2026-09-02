import json
import os
from app.services.tree_builder import PageIndexTreeBuilder
from app.services.tree_searcher import PageIndexTreeSearcher
from app.services.llm_service import generate_answer
from app.services.cache_manager import cache_manager
import logging

logger = logging.getLogger(__name__)
CACHE_DIR = "page_index_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

class PageIndexManager:
    def __init__(self):
        self.trees = {}
    
    async def add_large_document(self, file_bytes: bytes, filename: str):
        builder = PageIndexTreeBuilder(file_bytes, filename)
        tree = builder.build_tree()
        self.trees[filename] = tree
        with open(os.path.join(CACHE_DIR, filename.replace('.pdf', '.json')), 'w') as f:
            json.dump(tree, f)
    
    async def query_page_index(self, question: str, source_file: str) -> dict:
        if source_file not in self.trees:
            cache_path = os.path.join(CACHE_DIR, source_file.replace('.pdf', '.json'))
            try:
                with open(cache_path) as f:
                    self.trees[source_file] = json.load(f)
            except FileNotFoundError:
                return {"answer": f"Document '{source_file}' not found.", "pages": []}
        cached = cache_manager.get_from_query_cache(question, f"page_index_{source_file}")
        if cached:
            return cached
        searcher = PageIndexTreeSearcher(self.trees[source_file])
        best_node = await searcher.search(question)
        # Trong thực tế cần lấy nội dung từ trang best_node['page']
        node_content = f"Nội dung của {best_node['title']} (trang {best_node.get('page','?')})"
        answer = await generate_answer(question, node_content)
        page = best_node.get('page')
        if page:
            answer += f"\n\n(Tham khảo trang {page})"
        result = {"answer": answer, "pages": [page] if page else []}
        cache_manager.set_query_cache(question, f"page_index_{source_file}", result)
        return result

page_index_manager = PageIndexManager()