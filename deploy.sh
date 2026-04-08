#!/bin/bash
# =============================================================================
# deploy.sh — One-command deployment
# =============================================================================
# Usage:
#   ./deploy.sh cloudflare    # Cloudflare Tunnel (temp, free, instant)
#   ./deploy.sh worker        # Cloudflare Workers
#   ./deploy.sh railway       # Railway
#   ./deploy.sh render        # Render.com

set -e

COMMAND="${1:-cloudflare}"

echo "🚀 Deploying F.R.I.D.A.Y. via: $COMMAND"

case "$COMMAND" in
  cloudflare)
    echo "📡 Starting Cloudflare Tunnel (temp hosting — no server needed)..."
    if ! command -v cloudflared &>/dev/null; then
      echo "Installing cloudflared..."
      brew install cloudflare/cloudflare/cloudflared 2>/dev/null || \
      curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64 -o /usr/local/bin/cloudflared && chmod +x /usr/local/bin/cloudflared
    fi
    echo "🌐 Starting MCP server..."
    uv run friday &
    SERVER_PID=$!
    sleep 3
    echo "🔗 Starting Cloudflare Tunnel..."
    cloudflared tunnel --url http://localhost:8000 --no-autoupdate
    kill $SERVER_PID 2>/dev/null || true
    ;;

  worker)
    echo "☁️  Deploying to Cloudflare Workers..."
    echo "⚠️  Set secrets first:"
    echo "   npx wrangler secret put GROQ_API_KEY"
    echo "   npx wrangler secret put GOOGLE_API_KEY"
    npx wrangler deploy
    ;;

  railway)
    echo "🚂 Deploying to Railway..."
    if ! command -v railway &>/dev/null; then
      echo "Install Railway CLI: npm i -g @railway/cli"
      exit 1
    fi
    railway login
    railway init
    railway up
    ;;

  render)
    echo "🎨 Deploying to Render..."
    echo "⚠️  Create account at render.com, connect GitHub repo"
    echo "   Set Start Command: uv run friday"
    echo "   Add env vars from .env.example"
    echo ""
    echo "Or use render.yaml for declarative config."
    ;;

  docker)
    echo "🐳 Building Docker image..."
    docker build -t friday-mcp .
    docker run -p 8000:8000 --env-file .env friday-mcp
    ;;

  *)
    echo "Usage: ./deploy.sh [cloudflare|worker|railway|render|docker]"
    echo ""
    echo "  cloudflare  — Free temp URL via Cloudflare Tunnel (no server)"
    echo "  worker      — Deploy MCP server to Cloudflare Workers"
    echo "  railway     — Deploy to Railway ($5/mo, zero-config)"
    echo "  render      — Deploy to Render (free tier available)"
    echo "  docker      — Build and run Docker container"
    exit 1
    ;;
esac

echo "✅ Done!"
