#!/bin/bash
# =============================================================================
# F.R.I.D.A.Y. — Uninstall Script
# Removes app, shortcuts, and auto-start
# =============================================================================

echo ""
echo "  ╔══════════════════════════════════════════════════════════════╗"
echo "  ║       F.R.I.D.A.Y. — Uninstall                         ║"
echo "  ╚══════════════════════════════════════════════════════════════╝"
echo ""

APP_DIR="$HOME/Applications/F.R.I.D.A.Y..app"
LAUNCH_AGENT="$HOME/Library/LaunchAgents/com.friday.ai.agent.plist"

echo "  Removing F.R.I.D.A.Y. from auto-start..."
launchctl unload "$LAUNCH_AGENT" 2>/dev/null || true
rm -f "$LAUNCH_AGENT"
echo "  ✓ Auto-start removed"

echo ""
echo "  Removing Desktop shortcut..."
rm -f "$HOME/Desktop/F.R.I.D.A.Y..app"
echo "  ✓ Desktop shortcut removed"

echo ""
echo "  Removing application..."
rm -rf "$APP_DIR"
echo "  ✓ App removed"

echo ""
echo "  ╔══════════════════════════════════════════════════════════════╗"
echo "  ║  ✅ F.R.I.D.A.Y. has been uninstalled.              ║"
echo "  ╚══════════════════════════════════════════════════════════════╝"
echo ""
