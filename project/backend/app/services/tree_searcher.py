from typing import Dict
from app.services.llm_service import generate_llm_decision

class PageIndexTreeSearcher:
    def __init__(self, tree: Dict):
        self.tree = tree
    
    async def search(self, question: str, current_node: Dict = None) -> Dict:
        if current_node is None:
            current_node = self.tree
        if not current_node.get("children"):
            return current_node
        desc = "\n".join([f"- {c['title']} (page {c.get('page','?')})" for c in current_node["children"]])
        prompt = f"Question: {question}\nSections:\n{desc}\nOutput the most relevant section title exactly or 'NONE':"
        decision = await generate_llm_decision(prompt)
        decision = decision.strip()
        if decision == "NONE" or decision not in [c["title"] for c in current_node["children"]]:
            return current_node
        child = next(c for c in current_node["children"] if c["title"] == decision)
        return await self.search(question, child)