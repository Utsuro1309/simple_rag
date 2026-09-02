from sentence_transformers import CrossEncoder
import logging

logger = logging.getLogger(__name__)

class CrossEncoderReranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)
    
    def rerank(self, query: str, documents: list) -> list:
        if not documents:
            return []
        pairs = [(query, doc["content"]) for doc in documents]
        scores = self.model.predict(pairs)
        for i, score in enumerate(scores):
            documents[i]["relevance_score"] = float(score)
        return sorted(documents, key=lambda x: x["relevance_score"], reverse=True)