import os
import shutil
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from memory import Memory
from vision import analyze_image
from web_search import web_research
from agent import run_agent, run_coding, run_creation

load_dotenv()

BASE = Path(__file__).resolve().parent
UPLOADS = BASE / "uploads"
PROJECTS = BASE / "projects"
UPLOADS.mkdir(exist_ok=True)
PROJECTS.mkdir(exist_ok=True)

app = FastAPI(title="AK AI", version="2026.1")
memory = Memory(BASE / "memory.json")

class ChatRequest(BaseModel):
    message: str
    mode: str = "chat"
    use_web: bool = False

class MemoryRequest(BaseModel):
    text: str

@app.get("/")
async def home():
    return FileResponse(BASE / "index.html")

@app.get("/health")
async def health():
    return {"ok": True, "name": "AK AI"}

@app.post("/chat")
async def chat(req: ChatRequest):
    msg = req.message.strip()
    if not msg:
        raise HTTPException(400, "Message is empty")

    context = memory.relevant(msg)

    if req.mode == "coding":
        reply = await run_coding(msg, context)
    elif req.mode == "create":
        reply = await run_creation(msg, context)
    elif req.use_web or req.mode == "research":
        reply = await web_research(msg)
    elif req.mode == "agent":
        reply = await run_agent(msg, context, agent_mode=True)
    else:
        reply = await run_agent(msg, context)

    memory.add("user", msg)
    memory.add("assistant", reply)
    return {"reply": reply, "mode": req.mode}

@app.post("/vision")
async def vision(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "Please upload an image")
    data = await file.read()
    return {"reply": await analyze_image(data, file.content_type)}

@app.post("/files")
async def files(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "Filename missing")
    safe = Path(file.filename).name
    destination = UPLOADS / f"{uuid.uuid4().hex[:8]}_{safe}"
    with destination.open("wb") as out:
        shutil.copyfileobj(file.file, out)
    return {
        "filename": safe,
        "stored_as": destination.name,
        "size": destination.stat().st_size,
        "message": "File uploaded successfully."
    }

@app.get("/memory")
async def get_memory():
    return {"items": memory.recent(50)}

@app.post("/memory")
async def add_memory(req: MemoryRequest):
    if not req.text.strip():
        raise HTTPException(400, "Memory text is empty")
    memory.add("memory", req.text.strip())
    return {"ok": True}

@app.delete("/memory")
async def clear_memory():
    memory.clear()
    return {"ok": True}

@app.get("/projects")
async def list_projects():
    return {"projects": [p.name for p in PROJECTS.iterdir() if p.is_dir()]}

app.mount("/static", StaticFiles(directory=BASE), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=os.getenv("HOST", "0.0.0.0"),
                port=int(os.getenv("PORT", "8000")), reload=False)
