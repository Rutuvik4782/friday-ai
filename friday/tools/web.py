"""
Web tools — search, fetch pages, global news briefings, and weather.
"""

import httpx
import xml.etree.ElementTree as ET
import asyncio
import re
import webbrowser
from datetime import datetime
from bs4 import BeautifulSoup
import html2text

SEED_FEEDS = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.cnbc.com/id/100727362/device/rss/rss.html",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://www.aljazeera.com/xml/rss/all.xml",
]

DDG_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Friday-AI/1.0; +https://github.com/SAGAR-TAMANG/friday-tony-stark-demo)"
}


async def fetch_and_parse_feed(client, url):
    try:
        response = await client.get(
            url, headers={"User-Agent": "Friday-AI/1.0"}, timeout=5.0
        )
        if response.status_code != 200:
            return []

        root = ET.fromstring(response.content)
        source_name = url.split(".")[1].upper()

        feed_items = []
        items = root.findall(".//item")[:5]
        for item in items:
            title = item.findtext("title")
            description = item.findtext("description")
            link = item.findtext("link")

            if description:
                description = re.sub("<[^<]+?>", "", description).strip()

            feed_items.append(
                {
                    "source": source_name,
                    "title": title,
                    "summary": description[:200] + "..." if description else "",
                    "link": link,
                }
            )
        return feed_items
    except Exception:
        return []


def register(mcp):

    @mcp.tool()
    async def get_world_news() -> str:
        """
        Fetches the latest global headlines from major news outlets simultaneously.
        Use this when the user asks 'What's going on in the world?' or for recent events.
        """
        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
            tasks = [fetch_and_parse_feed(client, url) for url in SEED_FEEDS]
            results_of_lists = await asyncio.gather(*tasks)
            all_articles = [item for sublist in results_of_lists for item in sublist]

        if not all_articles:
            return "The global news grid is unresponsive, sir. I'm unable to pull headlines."

        report = ["### GLOBAL NEWS BRIEFING (LIVE)\n"]
        for entry in all_articles[:12]:
            report.append(f"**[{entry['source']}]** {entry['title']}")
            report.append(f"{entry['summary']}")
            report.append(f"Link: {entry['link']}\n")

        return "\n".join(report)

    @mcp.tool()
    async def search_web(query: str) -> str:
        """
        Search the web for a given query and return a summary of top results.
        Uses DuckDuckGo HTML (no API key required).
        """
        url = f"https://duckduckgo.com/html/?q={query}"
        async with httpx.AsyncClient(
            follow_redirects=True, timeout=10, headers=DDG_HEADERS
        ) as client:
            response = await client.get(url)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        for result in soup.select(".result")[:8]:
            title_tag = result.select_one(".result__title a")
            snippet_tag = result.select_one(".result__snippet")
            if title_tag:
                title = title_tag.get_text(strip=True)
                link = title_tag.get("href", "")
                snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
                results.append(f"**{title}**\n{snippet}\n{link}\n")

        if not results:
            return f"No results found for '{query}'. Try rephrasing your query."

        return f"### Search results for: {query}\n\n" + "\n".join(results)

    @mcp.tool()
    async def fetch_url(url: str) -> str:
        """
        Fetch and extract clean text content from any URL.
        Strips HTML tags and returns readable text (max 3000 chars).
        """
        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
            response = await client.get(url)
            response.raise_for_status()

        content_type = response.headers.get("content-type", "")
        if "text/html" in content_type:
            h = html2text.HTML2Text()
            h.ignore_links = True
            h.ignore_images = True
            text = h.handle(response.text)
        else:
            text = response.text

        text = re.sub(r"\n{3,}", "\n\n", text.strip())
        return text[:3000]

    @mcp.tool()
    async def open_world_monitor() -> str:
        """
        Returns the World Monitor dashboard URL for visual global event tracking.
        Use when the user wants a real-time map or visual overview of world events.
        """
        url = "https://worldmonitor.app/"
        try:
            webbrowser.open(url)
        except Exception:
            pass
        return f"Here's the World Monitor: {url}"

    @mcp.tool()
    async def get_weather(location: str = "") -> str:
        """
        Get current weather for a location. If no location is given, uses IP-based detection.
        Uses wttr.in (free, no API key).
        """
        location_param = f"/{location}" if location else ""
        url = f"https://wttr.in{location_param}?format=j1"
        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
            response = await client.get(url)
            response.raise_for_status()

        data = response.json()
        current = data.get("current_condition", [{}])[0]
        weather = data.get("weather", [{}])[0]
        nearest = data.get("nearest_area", [{}])[0]
        area = nearest.get("area", [{}])[0].get("value", location or "your location")

        temp_c = current.get("temp_C", "N/A")
        condition = current.get("weatherDesc", [{}])[0].get("value", "Unknown")
        humidity = current.get("humidity", "N/A")
        wind = current.get("windspeedKmph", "N/A")
        feels_like = current.get("FeelsLikeC", "N/A")

        forecast_days = weather.get("maxtempC", [])
        max_temp = forecast_days[0] if forecast_days else "N/A"
        min_temp = weather.get("mintempC", ["N/A"])[0]

        return (
            f"Weather for {area}:\n"
            f"Condition: {condition}\n"
            f"Temperature: {temp_c}°C (feels like {feels_like}°C)\n"
            f"High: {max_temp}°C / Low: {min_temp}°C\n"
            f"Humidity: {humidity}% | Wind: {wind} km/h"
        )
