import os
import httpx

async def web_research(query):
    key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("AI_MODEL", "gpt-6")
    if not key:
        return "OPENAI_API_KEY is missing."

    payload = {
        "model": model,
        "tools": [{"type": "web_search_preview"}],
        "input": query
    }

    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(
            "https://api.openai.com/v1/responses",
            headers={"Authorization": f"Bearer {key}"},
            json=payload
        )
        if r.status_code >= 400:
            return f"Web research API error ({r.status_code}): {r.text}"
        return r.json().get("output_text", "No research result.")
