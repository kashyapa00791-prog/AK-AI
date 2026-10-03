# AK AI

Modern personal AI assistant starter project for Android/Termux.

## Features
- Hindi / English / Hinglish chat
- Contextual memory with user controls
- Voice input in supported browsers
- Camera/image understanding
- File upload
- Web research mode
- Coding mode
- Creation mode
- Agent mode
- Projects area
- Privacy/memory controls
- Configurable AI model through `.env`

## Start

1. Copy `.env.example` to `.env`
2. Put your API key in `.env`
3. Install dependencies:
   `pip install -r requirements.txt`
4. Start:
   `python main.py`
5. Open:
   `http://127.0.0.1:8000`

The model name is configurable. Use the exact model identifier available to your API account; do not assume that a product name is automatically a valid API model identifier.
