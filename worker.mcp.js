/**
 * F.R.I.D.A.Y. MCP Server — Cloudflare Worker
 * ============================================
 * Wraps the FastMCP Python server behind a Cloudflare Worker.
 * Handles SSE transport for the LiveKit voice agent.
 *
 * Deploy:
 *   1. npx wrangler login
 *   2. npx wrangler secret put GOOGLE_API_KEY
 *   3. npx wrangler secret put GROQ_API_KEY
 *   4. npx wrangler deploy
 */

const PYTHON_SERVER = "http://127.0.0.1:8000";

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (url.pathname === "/sse" || url.pathname.endsWith("/sse")) {
      return handleSSE(request);
    }

    if (url.pathname === "/health") {
      return new Response(JSON.stringify({
        status: "online",
        service: "friday-mcp",
        timestamp: new Date().toISOString(),
      }), {
        headers: { "Content-Type": "application/json" },
      });
    }

    return new Response("F.R.I.D.A.Y. MCP Server — alive and ready.", {
      status: 200,
      headers: { "Content-Type": "text/plain" },
    });
  },
};

async function handleSSE(request) {
  const targetUrl = `${PYTHON_SERVER}/sse`;

  try {
    const response = await fetch(targetUrl, {
      method: "GET",
      headers: {
        "Accept": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
      },
    });

    return new Response(response.body, {
      status: response.status,
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Access-Control-Allow-Origin": "*",
        "X-Accel-Buffering": "no",
      },
    });
  } catch (err) {
    return new Response(JSON.stringify({
      error: "MCP server unreachable",
      message: err.message,
    }), {
      status: 503,
      headers: { "Content-Type": "application/json" },
    });
  }
}
