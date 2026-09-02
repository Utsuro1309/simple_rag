import tiktoken
from typing import List, Dict, Any

def assemble_context(chunks: List[Dict[str, Any]], max_tokens: int = 3500) -> str:
    encoding = tiktoken.get_encoding("cl100k_base")
    context_parts = []
    total_tokens = 0
    for chunk in chunks:
        source = chunk.get("source_file", "unknown")
        page = chunk.get("page_number", "unknown")
        tagged_text = f"[Source: {source}, page {page}]\n{chunk['content']}\n"
        chunk_tokens = len(encoding.encode(tagged_text))
        if total_tokens + chunk_tokens <= max_tokens:
            context_parts.append(tagged_text)
            total_tokens += chunk_tokens
        else:
            remaining = max_tokens - total_tokens
            if remaining > 100:
                truncated = truncate_text_by_tokens(chunk['content'], remaining - 50)
                if truncated:
                    context_parts.append(f"[Source: {source}, page {page}]\n{truncated}\n")
            break
    return "\n---\n".join(context_parts)

def truncate_text_by_tokens(text: str, max_tokens: int) -> str:
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    if len(tokens) <= max_tokens:
        return text
    return encoding.decode(tokens[:max_tokens]) + "..."