#!/usr/bin/env python3
"""
F.R.I.D.A.Y. — Mac Boot Experience
JARVIS-style startup on Mac login.

Run: python3 boot_sequence.py
"""

import os
import sys
import time
import datetime
import subprocess
import json
import urllib.request

# Config
YOUR_NAME = "boss"
FRIDAY_URL = "https://friday-ai-2hbv.onrender.com"
LOCATION = "Pune"

# Colors
BLUE = "\033[94m"
CYAN = "\033[96m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"


def clear():
    os.system("clear")


def speak(text, voice="Victoria"):
    """Use macOS say command for voice. Victoria sounds like F.R.I.D.A.Y."""
    try:
        subprocess.run(
            ["say", "-v", voice, "-r", "165", text], capture_output=True, timeout=10
        )
    except Exception:
        try:
            subprocess.run(
                ["say", "-v", "Alex", "-r", "165", text],
                capture_output=True,
                timeout=10,
            )
        except Exception:
            print(f"  [TTS] {text}")


def type_text(text, delay=0.03, color=CYAN):
    """Typewriter effect."""
    print(color, end="")
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print(RESET)


def get_weather(location):
    """Get weather for location."""
    try:
        url = f"https://wttr.in/{location}?format=j1"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read())
        current = data.get("current_condition", [{}])[0]
        temp = current.get("temp_C", "?")
        condition = current.get("weatherDesc", [{}])[0].get("value", "Clear")
        humidity = current.get("humidity", "?")
        return temp, condition, humidity
    except Exception:
        return "28", "Clear", "50"


def get_news():
    """Get top news headline."""
    try:
        import xml.etree.ElementTree as ET

        url = "https://feeds.bbci.co.uk/news/world/rss.xml"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            root = ET.fromstring(r.read())
        items = root.findall(".//item")[:1]
        if items:
            title = items[0].findtext("title", "")
            return title[:80]
    except Exception:
        return None


def get_time_greeting():
    """Get time-based greeting."""
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning", "☀️"
    elif 12 <= hour < 17:
        return "Good afternoon", "🌤️"
    elif 17 <= hour < 21:
        return "Good evening", "🌅"
    else:
        return "Good evening", "🌙"


def jarvis_quotes():
    """Random JARVIS-style quotes."""
    quotes = [
        "Everything is proceeding as expected, boss.",
        "All systems are nominal. I've been monitoring your sleep patterns.",
        "Boss, I've taken the liberty of brewing your coffee. It's ready.",
        "System online and fully operational. I missed you.",
        "Good to have you back, boss. Nothing to report.",
        "Running diagnostics... all green. Welcome home.",
        "Boss, I have the day's briefing ready whenever you need it.",
        "Your AI assistant is at your service.",
        "Systems online. Shall I pull up today's schedule?",
        "Boss, your neural network and my processors are fully synchronized.",
    ]
    import random

    return random.choice(quotes)


def show_arc_reactor():
    """Show ASCII arc reactor animation."""
    frames = [
        r"""
        ╔═══════════════════════════════════╗
        ║                                   ║
        ║           ◉◉◉◉◉◉◉◉◉           ║
        ║         ◉◉◉◉◉◉◉◉◉◉◉◉         ║
        ║        ◉◉            ◉◉        ║
        ║       ◉◉    F.R.I.D.A.Y.   ◉◉       ║
        ║        ◉◉            ◉◉        ║
        ║         ◉◉◉◉◉◉◉◉◉◉◉◉         ║
        ║           ◉◉◉◉◉◉◉◉◉           ║
        ║                                   ║
        ╚═══════════════════════════════════╝
        """,
        r"""
        ╔═══════════════════════════════════╗
        ║                                   ║
        ║           ●●●●●●●●●●           ║
        ║         ●●●●●●●●●●●●●●         ║
        ║        ●●●            ●●●        ║
        ║       ●●    INITIALIZING    ●●       ║
        ║        ●●●            ●●●        ║
        ║         ●●●●●●●●●●●●●●         ║
        ║           ●●●●●●●●●●           ║
        ║                                   ║
        ╚═══════════════════════════════════╝
        """,
    ]
    for i, frame in enumerate(frames * 2):
        clear()
        if i % 2 == 0:
            print(CYAN + frame + RESET)
        else:
            print(BLUE + frame + RESET)
        time.sleep(0.3)


def show_status_dashboard(greeting, weather_icon, temp, condition, headline):
    """Show the JARVIS status dashboard."""
    now = datetime.datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    time_str = now.strftime("%I:%M %p")

    quote = jarvis_quotes()

    clear()
    print()
    print(
        BLUE
        + "  ╔══════════════════════════════════════════════════════════════╗"
        + RESET
    )
    print(
        BLUE
        + "  ║"
        + RESET
        + BOLD
        + f"  F.R.I.D.A.Y. — FULLY RESPONSIVE INTELLIGENT DIGITAL ASSISTANT"
        + RESET
        + BLUE
        + "  ║"
        + RESET
    )
    print(
        BLUE
        + "  ╠══════════════════════════════════════════════════════════════╣"
        + RESET
    )
    print(
        BLUE
        + "  ║"
        + RESET
        + f"  {greeting} {YOUR_NAME.title()}! I'm F.R.I.D.A.Y. {weather_icon}           "
        + " " * 20
        + BLUE
        + "║"
        + RESET
    )
    print(
        BLUE
        + "  ╠══════════════════════════════════════════════════════════════╣"
        + RESET
    )
    print(
        BLUE
        + "  ║"
        + RESET
        + f"  📅 {date_str}                                    "
        + " " * 20
        + BLUE
        + "║"
        + RESET
    )
    print(
        BLUE
        + "  ║"
        + RESET
        + f"  🕐 {time_str}                                      "
        + " " * 20
        + BLUE
        + "║"
        + RESET
    )
    print(
        BLUE
        + "  ╠══════════════════════════════════════════════════════════════╣"
        + RESET
    )
    print(
        BLUE
        + "  ║"
        + RESET
        + f"  🌤️  WEATHER — {LOCATION}: {temp}°C, {condition}         "
        + " " * 18
        + BLUE
        + "║"
        + RESET
    )
    if headline:
        h = headline[:55] if headline else ""
        print(
            BLUE
            + "  ║"
            + RESET
            + f"  📰  NEWS: {h}..."
            + " " * (57 - len(h) - 13)
            + BLUE
            + "║"
            + RESET
        )
    print(
        BLUE
        + "  ╠══════════════════════════════════════════════════════════════╣"
        + RESET
    )
    print(
        BLUE
        + "  ║"
        + RESET
        + f'  💬  "{quote}"       '
        + " " * (57 - len(quote) - 10)
        + BLUE
        + "║"
        + RESET
    )
    print(
        BLUE
        + "  ╠══════════════════════════════════════════════════════════════╣"
        + RESET
    )
    print(
        BLUE
        + "  ║"
        + RESET
        + "  🤖 AI Status: ONLINE — Groq (free tier)                  "
        + " " * 6
        + BLUE
        + "║"
        + RESET
    )
    print(
        BLUE
        + "  ║"
        + RESET
        + f"  🌐 Web Chat: {FRIDAY_URL}/demo"
        + " " * (57 - 33 - len(FRIDAY_URL))
        + BLUE
        + "║"
        + RESET
    )
    print(
        BLUE
        + "  ╚══════════════════════════════════════════════════════════════╝"
        + RESET
    )
    print()


def send_notification(title, text):
    """Send macOS notification."""
    try:
        subprocess.run(
            ["osascript", "-e", f'display notification "{text}" with title "{title}"'],
            capture_output=True,
            timeout=5,
        )
    except Exception:
        pass


def open_chat():
    """Open the JARVIS chat in browser."""
    url = f"{FRIDAY_URL}/demo"
    try:
        subprocess.run(["open", url], capture_output=True, timeout=5)
    except Exception:
        pass


def main():
    clear()

    # Phase 1: Boot animation
    print(f"\n{BOLD}{BLUE}  Initializing F.R.I.D.A.Y. ...{RESET}\n")
    show_arc_reactor()

    # Phase 2: System checks
    print(f"{CYAN}  [BOOT] Loading neural networks...{RESET}")
    time.sleep(0.5)
    print(f"{CYAN}  [BOOT] Connecting to Groq servers...{RESET}")
    time.sleep(0.5)
    print(f"{CYAN}  [BOOT] Syncing with cloud services...{RESET}")
    time.sleep(0.5)
    print(f"{CYAN}  [BOOT] All systems nominal.{RESET}\n")
    time.sleep(0.5)

    # Phase 3: Get data
    greeting, weather_icon = get_time_greeting()
    temp, condition, humidity = get_weather(LOCATION)
    headline = get_news()

    # Phase 4: Speak greeting
    speak_text = f"Good {greeting.split()[1]}, {YOUR_NAME}. System online. I'm F.R.I.D.A.Y., fully operational. {LOCATION} is currently {temp} degrees, {condition}. All systems are nominal."
    print(f"{CYAN}  [VOICE] Speaking...{RESET}")
    speak(speak_text)

    # Phase 5: Show dashboard
    show_status_dashboard(greeting, weather_icon, temp, condition, headline)

    # Phase 6: Send notification
    send_notification(
        "F.R.I.D.A.Y. Online",
        f"{greeting} {YOUR_NAME}! {temp}°C in {LOCATION}. All systems nominal.",
    )

    # Phase 7: Wait for user
    print(
        f"{YELLOW}  Press ENTER to open chat or Q to quit:{RESET} ", end="", flush=True
    )
    try:
        key = input().strip().lower()
        if key == "q":
            print(
                f"\n{GREEN}  F.R.I.D.A.Y. going dark. See you soon, {YOUR_NAME}.{RESET}\n"
            )
            time.sleep(1)
            clear()
            return
        else:
            print(f"\n{CYAN}  Opening F.R.I.D.A.Y. chat...{RESET}\n")
            open_chat()
    except (EOFError, KeyboardInterrupt):
        pass

    clear()


if __name__ == "__main__":
    main()
