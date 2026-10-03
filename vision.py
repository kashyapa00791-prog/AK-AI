import os
import base64
import httpx

async def analyze_image(image_bytes, mime_type="image/jpeg"):
    key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("VISION_MODEL", os.getenv("AI_MODEL", "gpt-6"))
    if not key:
        return "OPENAI_API_KEY is missing."

    encoded = base64.b64encode(image_bytes).decode()
    payload = {
        "model": model,
        "input": [{
            "role": "user",
            "content": [
                {"type": "input_text", "text":
                 "Analyze this image carefully. Explain visible objects, text, layout, charts or important details. If uncertain, say so."},
                {"type": "input_image",
                 "image_url": f"data:{mime_type};base64,{encoded}"}
            ]
        }]
    }
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(
            "https://api.openai.com/v1/responses",
            headers={"Authorization": f"Bearer {key}"},
            json=payload
        )
        if r.status_code >= 400:
            return f"Vision API error ({r.status_code}): {r.text}"
        return r.json().get("output_text", "No vision response.")
