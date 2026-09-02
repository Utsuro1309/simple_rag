import tiktoken
import re
from typing import List, Dict, Any

def num_tokens_from_string(string: str, encoding_name: str = "cl100k_base") -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    return len(encoding.encode(string))

def semantic_chunking(text: str, max_chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current = []
    curr_len = 0
    for sent in sentences:
        sent_len = len(sent.split())
        if curr_len + sent_len <= max_chunk_size:
            current.append(sent)
            curr_len += sent_len
        else:
            if current:
                chunk_text = " ".join(current)
                chunks.append({"text": chunk_text, "token_count": num_tokens_from_string(chunk_text)})
            overlap_sent = current[-1:] if current else []
            current = overlap_sent + [sent]
            curr_len = len(" ".join(current).split())
    if current:
        chunk_text = " ".join(current)
        chunks.append({"text": chunk_text, "token_count": num_tokens_from_string(chunk_text)})
    return chunks