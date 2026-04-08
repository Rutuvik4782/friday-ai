"""
Data resources — expose static content or dynamic data via MCP resources.
"""

import datetime
import platform


def register(mcp):

    @mcp.resource("friday://info")
    def server_info() -> str:
        """Returns basic info about this MCP server."""
        return (
            "Friday MCP Server\n"
            "A Tony Stark-inspired AI assistant.\n"
            "Built with FastMCP.\n"
            "Supports: web search, news, weather, code execution, ticketing."
        )

    @mcp.resource("friday://capabilities")
    def capabilities() -> str:
        """List all available tools and their purposes."""
        return (
            "F.R.I.D.A.Y. Toolset:\n"
            "- get_world_news: Fetch latest global headlines from BBC, CNBC, NYT, Al Jazeera\n"
            "- search_web: Search DuckDuckGo for any query\n"
            "- fetch_url: Extract clean text from any URL\n"
            "- open_world_monitor: Open worldmonitor.app for global event visualization\n"
            "- get_weather: Current weather for any location (wttr.in)\n"
            "- get_current_time: Current datetime in ISO 8601\n"
            "- get_system_info: OS, machine, Python version\n"
            "- create_ticket / list_tickets / update_ticket_status: Supabase ticketing\n"
            "- execute_code: Run Python code safely (sandboxed)\n"
            "- format_json: Pretty-print JSON strings\n"
            "- word_count: Count chars, words, lines in text\n"
        )

    @mcp.resource("friday://status")
    def status() -> str:
        """Return server uptime and system status."""
        now = datetime.datetime.now().isoformat()
        sys_info = {
            "os": platform.system(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        }
        return (
            f"Status: ONLINE\n"
            f"Server time: {now}\n"
            f"Platform: {sys_info['os']} ({sys_info['machine']})\n"
            f"Python: {sys_info['python']}\n"
            "All systems operational, boss."
        )
