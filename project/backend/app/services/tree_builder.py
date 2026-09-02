import json
import logging
from typing import List, Dict
from pypdf import PdfReader
import io

logger = logging.getLogger(__name__)

class PageIndexTreeBuilder:
    def __init__(self, file_bytes: bytes, filename: str):
        self.file_bytes = file_bytes
        self.filename = filename
        self.tree = {"filename": filename, "title": filename, "children": [], "page_map": {}}
    
    def extract_toc(self) -> List[Dict]:
        reader = PdfReader(io.BytesIO(self.file_bytes))
        toc = []
        if reader.outline:
            def process(outline, level=0):
                for item in outline:
                    if isinstance(item, list):
                        process(item, level+1)
                    else:
                        page_num = None
                        if hasattr(item, 'page_number'):
                            page_num = item.page_number
                        elif hasattr(item, 'destination') and hasattr(item.destination, 'page_number'):
                            page_num = item.destination.page_number
                        toc.append({"title": item.title, "level": level, "page": page_num})
            process(reader.outline)
        return toc
    
    def build_tree(self) -> Dict:
        toc = self.extract_toc()
        if not toc:
            logger.warning("No TOC, building from headings")
            return self._build_from_headings()
        root = {"title": self.filename, "children": []}
        stack = [(root, 0)]
        for item in toc:
            node = {"title": item["title"], "page": item["page"], "children": []}
            while len(stack) > item["level"] + 1:
                stack.pop()
            parent = stack[-1][0]
            parent["children"].append(node)
            stack.append((node, item["level"]+1))
            if item["page"]:
                self.tree["page_map"][item["title"]] = item["page"]
        self.tree["children"] = root["children"]
        return self.tree
    
    def _build_from_headings(self) -> Dict:
        reader = PdfReader(io.BytesIO(self.file_bytes))
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text()
        lines = full_text.split('\n')
        headings = []
        for i, line in enumerate(lines):
            if line.isupper() and len(line.split()) < 10:
                headings.append({"title": line.strip(), "level": 1, "page": i//50+1})
            elif line.strip().startswith(("Chapter", "Section", "1.", "2.", "3.")):
                headings.append({"title": line.strip(), "level": 2, "page": i//50+1})
        root = {"title": self.filename, "children": []}
        for h in headings:
            root["children"].append({"title": h["title"], "page": h["page"], "children": []})
        self.tree["children"] = root["children"]
        return self.tree