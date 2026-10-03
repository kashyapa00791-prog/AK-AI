import os
import httpx

SYSTEM = """You are AK AI, a modern multimodal personal AI assistant.
You communicate naturally in Hindi, English and Hinglish.
Understand conversation context and answer clearly.
Never claim an external action was completed unless the system actually performed it.
For sensitive or consequential actions, require explicit user confirmation.
When uncertain, say so.
You can help with reasoning, coding, projects, writing and planning."""

async def _response(instructions, inputs):
    key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("AI_MODEL", "gpt-6")
    if not key:
        return "OPENAI_API_KEY is missing. Add your API key to the .env file."

    payload = {"model": model, "instructions": instructions, "input": inputs}
    headers = {"Authorization": f"Bearer {key}"}

    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post("https://api.openai.com/v1/responses",
                              headers=headers, json=payload)
        if r.status_code >= 400:
            try:
                detail = r.json()
            except Exception:
                detail = r.text
            return f"API error ({r.status_code}): {detail}"
        data = r.json()
    return data.get("output_text", "No response returned.")

def _context(context):
    if not context:
        return "No previous relevant memory."
    return "\n".join(f'{x["role"]}: {x["content"]}' for x in context[-10:])

async def run_agent(message, context=None, agent_mode=False):
    extra = """
You are operating in agent mode. Break the user's goal into sensible steps,
use available capabilities conceptually, report progress when useful, and ask
for confirmation before sensitive external actions.
""" if agent_mode else ""
    instructions = SYSTEM + extra + "\nRelevant memory:\n" + _context(context)
    return await _response(instructions, [{"role": "user", "content": message}])

async def run_coding(message, context=None):
    instructions = SYSTEM + """
You are AK AI Coding mode. Analyze project structure, write complete code,
debug errors, explain fixes, and preserve existing requirements.
When giving a file, clearly identify its filename and provide complete content.
""" + "\nRelevant memory:\n" + _context(context)
    return await _response(instructions, [{"role": "user", "content": message}])

async def run_creation(message, context=None):
    instructions = SYSTEM + """
You are AK AI Creation mode. Help create prompts, scripts, websites,
documents, presentations and creative plans. Do not pretend to have generated
a file or image unless an actual generation tool has been connected.
""" + "\nRelevant memory:\n" + _context(context)
    return await _response(instructions, [{"role": "user", "content": message}])
