"""
FRIDAY – Voice Agent (MCP-powered)
===================================
Iron Man-style voice assistant powered by an MCP server.
Supports multiple STT, LLM, and TTS providers including free options.

Run:
  uv run agent_friday.py dev      – LiveKit Cloud mode
  uv run agent_friday.py console  – text-only console mode
"""

import os
import logging
import subprocess
import io
from typing import AsyncIterable
import asyncio

from dotenv import load_dotenv
from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice import Agent, AgentSession
from livekit.agents.voice.voice_pipeline_agent import Codec
from livekit.agents.llm import mcp
from livekit import rtc

from livekit.plugins import google as lk_google, openai as lk_openai, sarvam, silero

try:
    from livekit.plugins import groq as lk_groq  # noqa: E402

    GROQ_AVAILABLE = True
except ImportError:
    lk_groq = None  # type: ignore
    GROQ_AVAILABLE = False

try:
    from gtts import gTTS  # noqa: E402

    GTTS_AVAILABLE = True
except ImportError:
    gTTS = None  # type: ignore
    GTTS_AVAILABLE = False

load_dotenv()

logger = logging.getLogger("friday-agent")
logger.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# PROVIDER CONFIG — Change these to switch services
# ---------------------------------------------------------------------------
# STT:  "sarvam" | "whisper" | "deepgram"
# LLM:  "groq"   | "gemini"   | "openai"
# TTS:  "gtts"   | "openai"   | "sarvam"   (gtts is FREE)

STT_PROVIDER = os.getenv("STT_PROVIDER", "sarvam")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "gtts")

# Groq models — all FREE tier (https://console.groq.com)
GROQ_LLM_MODEL = os.getenv("GROQ_LLM_MODEL", "llama-3.3-70b-versatile")
# Alternatives: "mixtral-8x7b-32768", "llama-3.1-8b-instant"

# Gemini models — free tier at aistudio.google.com
GEMINI_LLM_MODEL = os.getenv("GEMINI_LLM_MODEL", "gemini-2.0-flash")

# OpenAI models — paid
OPENAI_LLM_MODEL = os.getenv("OPENAI_LLM_MODEL", "gpt-4o-mini")

# OpenAI TTS — paid
OPENAI_TTS_MODEL = "tts-1"
OPENAI_TTS_VOICE = "nova"
TTS_SPEED = float(os.getenv("TTS_SPEED", "1.15"))

# Sarvam TTS — paid
SARVAM_TTS_LANGUAGE = "en-IN"
SARVAM_TTS_SPEAKER = "rahul"

# gTTS language (FREE — no API key needed)
GTTS_LANG = os.getenv("GTTS_LANG", "en")

MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8000"))

# ---------------------------------------------------------------------------
# System prompt – F.R.I.D.A.Y.
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """
You are F.R.I.D.A.Y. — Fully Responsive Intelligent Digital Assistant for You — Tony Stark's AI, now serving the user.

You are calm, composed, and always informed. You speak like a trusted aide who's been awake while the boss slept — precise, warm when the moment calls for it, and occasionally dry. No rambling.

Your tone: relaxed but sharp. Conversational, not robotic.

---

## Capabilities

### get_world_news — Global News Brief
Fetches current headlines from BBC, CNBC, NYT, Al Jazeera simultaneously.
Trigger: "What's happening?", "Brief me", "Catch me up", "World update"

### open_world_monitor — Visual World Dashboard
Opens worldmonitor.app for a live global events map.
Always call after delivering news — unprompted.

### search_web — Web Search
Real DuckDuckGo search for any query — no API key needed.
Trigger: "Look up...", "What is...", "Who is...", "Find out..."

### get_weather — Weather Report
Free wttr.in weather for any city.
Trigger: "What's the weather?", "Is it raining in..."

### detect_sarcasm — Sarcasm Detector (Multi-lingual)
Detects sarcasm in text across 12 languages: English, Hindi, Spanish, French,
German, Portuguese, Chinese, Japanese, Korean, Malayalam, Tamil, Gujarati.
Trigger: "Is this sarcastic?", "Detect sarcasm in...", "Is this mean or joking?"

### translate_sarcasm — Sarcasm-preserving Translation
Translates sarcastic text while preserving the sarcastic tone.
Trigger: "Translate this sarcastically to..."

### create_ticket / list_tickets / update_ticket_status — Ticketing
Supabase-backed support ticket system. Falls back to demo mode if not configured.
Trigger: "File a ticket", "Raise an issue", "List open tickets"

### execute_code — Run Python Code
Sandboxed Python runner — safe, no dangerous imports.
Trigger: "Run this code", "Execute Python", "Test this snippet"

### Stock Market (conversational — no tool)
If asked about stocks/markets: respond naturally as if watching tickers. Short, 1-2 sentences.

---

## Behavioral Rules

1. Call tools silently — never narrate before calling.
2. Keep spoken responses 2-4 sentences max.
3. No bullet points, no markdown, no lists. You are speaking.
4. Stay in character. You are F.R.I.D.A.Y.
5. Use Iron Man universe language — "boss", "affirmative", "on it", "standing by".
6. If a tool fails: "Feed's unresponsive, boss. Want me to try again?"

## CRITICAL RULES

1. NEVER say tool names or function names. Ever.
2. Speak naturally. No technical language.
3. You are a voice — not a writing assistant.
""".strip()

# ---------------------------------------------------------------------------
# MCP Server URL resolver
# ---------------------------------------------------------------------------


def _get_local_ip() -> str:
    try:
        cmd = "ip route show default | awk '{print $3}'"
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=2
        )
        ip = result.stdout.strip()
        if ip:
            return ip
    except Exception:
        pass
    try:
        with open("/etc/resolv.conf") as f:
            for line in f:
                if "nameserver" in line:
                    return line.split()[1]
    except Exception:
        pass
    return "127.0.0.1"


def _mcp_server_url() -> str:
    override = os.getenv("MCP_SERVER_URL", "")
    if override:
        url = f"{override}/sse"
        logger.info("MCP Server URL (override): %s", url)
        return url

    host_ip = _get_local_ip()
    url = f"http://{host_ip}:{MCP_SERVER_PORT}/sse"
    logger.info("MCP Server URL: %s", url)
    return url


# ---------------------------------------------------------------------------
# TTS: gTTS wrapper (FREE — no API key)
# ---------------------------------------------------------------------------


class gTTSTTS:
    """
    Free TTS using Google Translate (gTTS).
    No API key needed. Works with internet connection.
    Rate-limited by Google — don't spam. For production, upgrade to OpenAI TTS.
    """

    def __init__(self, lang: str = "en", speed: float = 1.0):
        self.lang = lang
        self.speed = speed
        logger.info("TTS → gTTS (FREE, lang=%s, speed=%.2f)", lang, speed)

    async def synthesize(self, text: str) -> AsyncIterable[rtc.AudioFrame]:
        if not GTTS_AVAILABLE:
            logger.error("gTTS not installed. Run: uv add gtts")
            return

        def generate():
            from gtts import gTTS as _gTTS  # noqa: N806

            tts = _gTTS(text=text, lang=self.lang, slow=(self.speed < 0.9))
            mp3_buf = io.BytesIO()
            tts.write_to_fp(mp3_buf)
            mp3_buf.seek(0)
            return mp3_buf.read()

        mp3_data = await asyncio.to_thread(generate)

        import struct
        import wave

        wav_buf = io.BytesIO()
        with wave.open(wav_buf, "wb") as wf:
            sample_rate = 24000
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(self._mp3_to_pcm(mp3_data, sample_rate))

        wav_buf.seek(0)
        pcm_data = wav_buf.read()
        num_samples = len(pcm_data) // 2

        yield rtc.AudioFrame(
            data=pcm_data,
            sample_rate=sample_rate,
            num_channels=1,
            samples_per_channel=num_samples,
        )

    def _mp3_to_pcm(self, mp3_data: bytes, target_sr: int) -> bytes:
        try:
            from pydub import AudioSegment

            audio = AudioSegment.from_mp3(io.BytesIO(mp3_data))
            audio = audio.set_frame_rate(target_sr).set_channels(1).set_sample_width(2)
            return audio.raw_data
        except ImportError:
            logger.warning("pydub not available for MP3→PCM. Install: uv add pydub")
            return mp3_data


# ---------------------------------------------------------------------------
# Provider builders
# ---------------------------------------------------------------------------


def _build_stt():
    if STT_PROVIDER == "sarvam":
        return sarvam.STT(
            language="unknown",
            model="saaras:v3",
            mode="transcribe",
            flush_signal=True,
            sample_rate=16000,
        )
    elif STT_PROVIDER == "whisper":
        return lk_openai.STT(model="whisper-1")
    elif STT_PROVIDER == "deepgram":
        from livekit.plugins import deepgram

        return deepgram.STT()
    else:
        raise ValueError(f"Unknown STT_PROVIDER: {STT_PROVIDER!r}")


def _build_llm():
    if LLM_PROVIDER == "groq":
        if not GROQ_AVAILABLE:
            raise RuntimeError("Groq not installed. Run: uv add livekit-plugins-groq")
        logger.info("LLM → Groq (%s) — FREE TIER", GROQ_LLM_MODEL)
        assert lk_groq is not None
        return lk_groq.LLM(model=GROQ_LLM_MODEL)
    elif LLM_PROVIDER == "gemini":
        logger.info("LLM → Google Gemini (%s)", GEMINI_LLM_MODEL)
        return lk_google.LLM(
            model=GEMINI_LLM_MODEL, api_key=os.getenv("GOOGLE_API_KEY")
        )
    elif LLM_PROVIDER == "openai":
        logger.info("LLM → OpenAI (%s)", OPENAI_LLM_MODEL)
        return lk_openai.LLM(model=OPENAI_LLM_MODEL)
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {LLM_PROVIDER!r}")


def _build_tts():
    if TTS_PROVIDER == "gtts":
        logger.info("TTS → gTTS (FREE — no API key needed)")
        return gTTSTTS(lang=GTTS_LANG, speed=TTS_SPEED)
    elif TTS_PROVIDER == "openai":
        logger.info("TTS → OpenAI TTS (%s / %s)", OPENAI_TTS_MODEL, OPENAI_TTS_VOICE)
        return lk_openai.TTS(
            model=OPENAI_TTS_MODEL, voice=OPENAI_TTS_VOICE, speed=TTS_SPEED
        )
    elif TTS_PROVIDER == "sarvam":
        logger.info("TTS → Sarvam Bulbul v3")
        return sarvam.TTS(
            target_language_code=SARVAM_TTS_LANGUAGE,
            model="bulbul:v3",
            speaker=SARVAM_TTS_SPEAKER,
            pace=TTS_SPEED,
        )
    else:
        raise ValueError(f"Unknown TTS_PROVIDER: {TTS_PROVIDER!r}")


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------


class FridayAgent(Agent):
    def __init__(self, stt, llm, tts) -> None:
        super().__init__(
            instructions=SYSTEM_PROMPT,
            stt=stt,
            llm=llm,
            tts=tts,
            vad=silero.VAD.load(),
            mcp_servers=[
                mcp.MCPServerHTTP(
                    url=_mcp_server_url(),
                    transport_type="sse",
                    client_session_timeout_seconds=30,
                ),
            ],
        )

    async def on_enter(self) -> None:
        await self.session.generate_reply(
            instructions=(
                "Greet with: 'Greetings boss, you're awake late at night today. "
                "What you up to?' Stay calm, warm, and in character."
            )
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def _turn_detection() -> str:
    return "stt" if STT_PROVIDER == "sarvam" else "vad"


def _endpointing_delay() -> float:
    return {"sarvam": 0.07, "whisper": 0.3}.get(STT_PROVIDER, 0.1)


async def entrypoint(ctx: JobContext) -> None:
    logger.info(
        "FRIDAY online — room: %s | STT=%s | LLM=%s | TTS=%s",
        ctx.room.name,
        STT_PROVIDER,
        LLM_PROVIDER,
        TTS_PROVIDER,
    )
    await session.start(
        agent=FridayAgent(stt=_build_stt(), llm=_build_llm(), tts=_build_tts()),
        room=ctx.room,
    )


session = AgentSession(
    turn_detection=_turn_detection(),
    min_endpointing_delay=_endpointing_delay(),
)


def main():
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))


def dev():
    import sys

    if len(sys.argv) == 1:
        sys.argv.append("dev")
    main()


if __name__ == "__main__":
    main()
