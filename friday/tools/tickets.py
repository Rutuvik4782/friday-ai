"""
Ticketing tools — create, list, and update tickets via Supabase.
"""

import os
import httpx
from datetime import datetime


def register(mcp):

    @mcp.tool()
    async def create_ticket(
        title: str, description: str, priority: str = "medium", status: str = "open"
    ) -> str:
        """
        Create a new support ticket. Sends it to Supabase if configured, otherwise returns a mock response.
        Args:
            title: Short title of the issue
            description: Detailed description
            priority: low | medium | high | critical
            status: open | in_progress | resolved | closed
        """
        supabase_url = os.getenv("SUPABASE_URL", "")
        supabase_key = os.getenv("SUPABASE_API_KEY", "")

        ticket_data = {
            "title": title,
            "description": description,
            "priority": priority,
            "status": status,
            "created_at": datetime.utcnow().isoformat(),
        }

        if supabase_url and supabase_key and "your-project" not in supabase_url:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    supabase_url,
                    json=ticket_data,
                    headers={
                        "apikey": supabase_key,
                        "Authorization": f"Bearer {supabase_key}",
                        "Content-Type": "application/json",
                        "Prefer": "return=representation",
                    },
                )
                if response.status_code in (200, 201):
                    result = response.json()
                    ticket_id = (
                        result[0].get("id", "unknown")
                        if isinstance(result, list)
                        else result.get("id", "unknown")
                    )
                    return f"Ticket #{ticket_id} created successfully.\nTitle: {title}\nPriority: {priority}\nStatus: {status}"
                else:
                    return f"Ticket creation failed: {response.status_code} — {response.text}"

        ticket_id = f"MOCK-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        return (
            f"[Demo mode] Ticket created (Supabase not configured):\n"
            f"ID: {ticket_id}\n"
            f"Title: {title}\n"
            f"Description: {description}\n"
            f"Priority: {priority}\n"
            f"Status: {status}"
        )

    @mcp.tool()
    async def list_tickets(status: str = "open", limit: int = 10) -> str:
        """
        List support tickets filtered by status.
        Args:
            status: open | in_progress | resolved | closed (default: open)
            limit: max number of tickets to return (default: 10)
        """
        supabase_url = os.getenv("SUPABASE_URL", "")
        supabase_key = os.getenv("SUPABASE_API_KEY", "")

        if supabase_url and supabase_key and "your-project" not in supabase_url:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    f"{supabase_url}?status=eq.{status}&limit={limit}&order=created_at.desc",
                    headers={
                        "apikey": supabase_key,
                        "Authorization": f"Bearer {supabase_key}",
                    },
                )
                if response.status_code == 200:
                    tickets = response.json()
                    if not tickets:
                        return f"No {status} tickets found."
                    lines = [f"### {status.upper()} Tickets\n"]
                    for t in tickets:
                        lines.append(
                            f"**#{t.get('id')}** — {t.get('title')} "
                            f"[{t.get('priority')} priority]"
                        )
                    return "\n".join(lines)
                return f"Failed to fetch tickets: {response.status_code}"

        mock_tickets = [
            {"id": "MOCK-001", "title": "Server latency spike", "priority": "high"},
            {
                "id": "MOCK-002",
                "title": "Dashboard loading slowly",
                "priority": "medium",
            },
            {"id": "MOCK-003", "title": "Login timeout issue", "priority": "high"},
        ]
        lines = [f"[Demo mode] {status.upper()} Tickets:\n"]
        for t in mock_tickets[:limit]:
            lines.append(f"**{t['id']}** — {t['title']} [{t['priority']} priority]")
        return "\n".join(lines)

    @mcp.tool()
    async def update_ticket_status(ticket_id: str, status: str) -> str:
        """
        Update the status of an existing ticket.
        Args:
            ticket_id: The ticket ID to update
            status: new status — open | in_progress | resolved | closed
        """
        supabase_url = os.getenv("SUPABASE_URL", "")
        supabase_key = os.getenv("SUPABASE_API_KEY", "")

        if supabase_url and supabase_key and "your-project" not in supabase_url:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.patch(
                    f"{supabase_url}?id=eq.{ticket_id}",
                    json={
                        "status": status,
                        "updated_at": datetime.utcnow().isoformat(),
                    },
                    headers={
                        "apikey": supabase_key,
                        "Authorization": f"Bearer {supabase_key}",
                        "Content-Type": "application/json",
                    },
                )
                if response.status_code in (200, 204):
                    return f"Ticket #{ticket_id} updated to status: {status}"
                return f"Update failed: {response.status_code} — {response.text}"

        return f"[Demo mode] Ticket #{ticket_id} updated to status: {status}"
