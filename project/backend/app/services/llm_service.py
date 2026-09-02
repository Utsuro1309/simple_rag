from openai import AsyncOpenAI
from app.config import Config
import logging

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)

async def generate_answer(question: str, context: str) -> str:
    prompt = f"""You are an AI assistant. Answer the question based ONLY on the provided context.
If the context doesn't contain the answer, say "I don't have enough information."

Context:
{context}

Question: {question}
Answer:"""
    try:
        response = await client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"LLM failed: {e}")
        return "Sorry, an error occurred."

async def generate_llm_decision(prompt: str) -> str:
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=50
    )
    return response.choices[0].message.content