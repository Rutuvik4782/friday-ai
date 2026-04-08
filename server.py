"""
Friday MCP Server — Entry Point
Serves both:
  - SSE transport for LiveKit voice agent (MCP protocol)
  - HTTP REST for web demo (chat, health)

Run with: uv run friday
"""

import os
import json
import asyncio
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

from mcp.server.fastmcp import FastMCP
from friday.tools import register_all_tools
from friday.prompts import register_all_prompts
from friday.resources import register_all_resources
from friday.config import config

mcp = FastMCP(
    name=config.SERVER_NAME,
    instructions=(
        "You are Friday, a Tony Stark-style AI assistant. "
        "You have access to a set of tools to help the user. "
        "Be concise, accurate, and a little witty."
    ),
)

register_all_tools(mcp)
register_all_prompts(mcp)
register_all_resources(mcp)

# ---------------------------------------------------------------------------
# HTTP endpoints for web demo (runs alongside SSE)
# ---------------------------------------------------------------------------

from starlette.applications import Starlette
from starlette.responses import JSONResponse, PlainTextResponse, FileResponse
from starlette.routing import Route, Mount
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import uvicorn

# Groq client for free LLM
try:
    from groq import Groq

    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


def _get_groq_client():
    if GROQ_AVAILABLE:
        return Groq(api_key=os.getenv("GROQ_API_KEY", ""))
    return None


SYSTEM_PROMPT_HTTP = """You are F.R.I.D.A.Y. — Fully Responsive Intelligent Digital Assistant for You.

You are calm, composed, and always informed. Think of yourself as a trusted aide who is precise, warm when the moment calls for it, and occasionally dry.

Keep responses SHORT — 2-4 sentences maximum. Conversational. Never robotic.
Use phrases like: "boss", "affirmative", "on it", "standing by".
Never use bullet points, markdown, or lists. You are speaking, not writing.

## Tools available:
- get_world_news: global news from BBC, CNBC, NYT, Al Jazeera
- search_web: DuckDuckGo search
- get_weather: weather for any city
- detect_sarcasm: sarcasm detection in 12 languages
- execute_code: run Python safely
- create_ticket: file a support ticket
"""


async def health(request):
    return JSONResponse(
        {
            "status": "online",
            "service": "F.R.I.D.A.Y. MCP Server",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": "operational",
            "groq_connected": _get_groq_client() is not None,
            "endpoints": ["/health", "/chat", "/sse"],
            "message": "All systems nominal, boss.",
        }
    )


async def chat(request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)

    messages = body.get("messages", [])
    llm = body.get("llm", os.getenv("LLM_PROVIDER", "groq"))
    user_message = messages[-1]["content"] if messages else ""

    # Build system-aware message list
    chat_messages = [{"role": "system", "content": SYSTEM_PROMPT_HTTP}]
    for m in messages[-10:]:  # last 10 messages
        chat_messages.append({"role": m.get("role", "user"), "content": m["content"]})

    client = _get_groq_client()

    if llm == "groq" and client:
        model = os.getenv("GROQ_LLM_MODEL", "llama-3.3-70b-versatile")
        try:
            response = client.chat.completions.create(
                model=model,
                messages=chat_messages,
                temperature=0.7,
                max_tokens=300,
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = f"Groq is having issues right now, boss. Try again in a moment. Error: {str(e)[:100]}"

    elif llm == "gemini" and os.getenv("GOOGLE_API_KEY"):
        reply = await _gemini_chat(chat_messages)

    else:
        reply = "No LLM configured. Set GROQ_API_KEY for free Groq or GOOGLE_API_KEY for Gemini in your .env file."

    return JSONResponse({"reply": reply, "model": llm})


async def _gemini_chat(messages):
    import httpx

    system = next((m["content"] for m in messages if m["role"] == "system"), "")
    user_text = next(
        (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
    )

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
            f"?key={os.getenv('GOOGLE_API_KEY')}",
            json={
                "contents": [{"parts": [{"text": user_text}]}],
                "systemInstruction": {"parts": [{"text": system}]},
                "generationConfig": {"maxOutputTokens": 300, "temperature": 0.7},
            },
        )
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]


async def call_tool(request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)

    tool_name = body.get("tool")
    arguments = body.get("arguments", {})

    if not tool_name:
        return JSONResponse({"error": "No tool specified"}, status_code=400)

    try:
        result = await mcp.call_tool(tool_name, arguments)
        if hasattr(result, "__iter__"):
            result = [str(item) for item in result]
        elif hasattr(result, "text"):
            result = result.text
        else:
            result = str(result)
        return JSONResponse({"result": result})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def list_tools_http(request):
    tools = await mcp.list_tools()
    return JSONResponse(
        {"tools": [{"name": t.name, "description": t.description[:100]} for t in tools]}
    )


async def root(request):
    return JSONResponse(
        {
            "name": "F.R.I.D.A.Y. MCP Server",
            "tagline": "Fully Responsive Intelligent Digital Assistant for You",
            "version": "1.0.0",
            "endpoints": {
                "/": "This info",
                "/health": "Server status",
                "/chat": "POST: Chat with F.R.I.D.A.Y. (needs .env with GROQ_API_KEY)",
                "/sse": "MCP SSE transport (for LiveKit voice agent)",
                "/tools": "List all available tools",
                "/call_tool": "POST: Call a specific tool",
            },
            "message": "Tony Stark approved. Operational.",
        }
    )


async def web_demo(request):
    return FileResponse("web_demo/index.html")


starlette_app = Starlette(
    routes=[
        Route("/", root),
        Route("/health", health),
        Route("/chat", chat, methods=["POST"]),
        Route("/tools", list_tools_http),
        Route("/call_tool", call_tool, methods=["POST"]),
        Route("/demo", web_demo),
        Route("/web_demo", web_demo),
        Mount("/sse", app=mcp.streamable_http_app()),
    ],
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ],
)

app = starlette_app


def main():
    print("=" * 60)
    print("  F.R.I.D.A.Y. — Tony Stark AI Assistant")
    print("  MCP Server + HTTP REST API")
    print("=" * 60)
    print("  🌐 HTTP API:  http://127.0.0.1:8000")
    print("  🔗 SSE/MCP:   http://127.0.0.1:8000/sse")
    print("  📊 Health:    http://127.0.0.1:8000/health")
    print("  💬 Chat:      POST http://127.0.0.1:8000/chat")
    print("=" * 60)
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(starlette_app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
