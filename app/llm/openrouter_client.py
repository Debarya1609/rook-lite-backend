# app/llm/openrouter_client.py

import os
import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-4o-mini"


def generate_analysis(prompt: str) -> str:
    response = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "You are a senior marketing analyst."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        },
        timeout=60
    )

    response.raise_for_status()
    data = response.json()

    content = (
        data.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
    )

    if not content or not content.strip():
        raise ValueError("LLM returned empty response")

    return content
