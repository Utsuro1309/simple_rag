import weaviate
import time
import logging
from app.config import Config

logger = logging.getLogger(__name__)

def get_client_with_retry(max_retries=10, delay=5):
    for attempt in range(max_retries):
        try:
            client = weaviate.Client(
                url=Config.WEAVIATE_URL,
                additional_headers={"X-OpenAI-Api-Key": Config.OPENAI_API_KEY}
            )
            # Kiểm tra kết nối
            client.get_meta()
            logger.info(f"Connected to Weaviate at {Config.WEAVIATE_URL}")
            return client
        except Exception as e:
            logger.warning(f"Attempt {attempt+1}/{max_retries} failed: {e}")
            time.sleep(delay)
    raise Exception("Could not connect to Weaviate after retries")

client = get_client_with_retry()

def init_schema():
    if client.schema.exists("Document"):
        client.schema.delete_class("Document")
    schema = {
        "class": "Document",
        "vectorizer": "text2vec-openai",
        "properties": [
            {"name": "content", "dataType": ["text"]},
            {"name": "source_file", "dataType": ["string"]},
            {"name": "doc_type", "dataType": ["string"]},
            {"name": "page_number", "dataType": ["int"]}
        ]
    }
    client.schema.create_class(schema)

# Các hàm helper giữ nguyên
def get_collection():
    return client

def near_text_search(query: str, limit: int = 10):
    result = (
        client.query
        .get("Document", ["content", "source_file", "doc_type", "page_number", "_additional {id}"])
        .with_near_text({"concepts": [query]})
        .with_limit(limit)
        .do()
    )
    return result["data"]["Get"]["Document"]

def bm25_search(query: str, limit: int = 10):
    result = (
        client.query
        .get("Document", ["content", "source_file", "doc_type", "page_number", "_additional {id}"])
        .with_bm25({"query": query})
        .with_limit(limit)
        .do()
    )
    return result["data"]["Get"]["Document"]