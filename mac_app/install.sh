#!/bin/bash
# =============================================================================
# F.R.I.D.A.Y. macOS App — Install Script
# =============================================================================

set -e

echo ""
echo "  ╔══════════════════════════════════════════════════════════╗"
echo "  ║     F.R.I.D.A.Y. — Native macOS App Installer        ║"
echo "  ╚══════════════════════════════════════════════════════════╝"
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$HOME/Applications/F.R.I.D.A.Y..app"

echo "  [1/5] Checking Python..."
if ! command -v python3 &>/dev/null; then
    echo "  ❌ Python 3 not found. Install from python.org"
    exit 1
fi
echo "  ✓ Python 3 found"

echo ""
echo "  [2/4] Installing dependencies..."
python3 -m pip install PyQt6 pyttsx3 sounddevice edge-tts --break-system-packages --quiet 2>/dev/null || \
python3 -m pip install PyQt6 pyttsx3 sounddevice edge-tts --break-system-packages
echo "  ✓ Dependencies installed"

echo ""
echo "  [3/4] Creating App bundle..."
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

cat > "$APP_DIR/Contents/MacOS/F.R.I.D.A.Y." << 'LAUNCHER'
#!/bin/bash
cd "$(dirname "$0")/.."
PYTHON=$(python3 -c 'import sys; print(sys.executable)')
exec "$PYTHON" "$(dirname "$0")/../Resources/friday_app.py" "$@"
LAUNCHER
chmod +x "$APP_DIR/Contents/MacOS/F.R.I.D.A.Y."

cp "$SCRIPT_DIR/friday_app.py" "$APP_DIR/Contents/Resources/"
cp "$SCRIPT_DIR/voice_helper.swift" "$APP_DIR/Contents/Resources/"

cat > "$APP_DIR/Contents/Info.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key><string>F.R.I.D.A.Y.</string>
    <key>CFBundleDisplayName</key><string>F.R.I.D.A.Y.</string>
    <key>CFBundleIdentifier</key><string>com.friday.ai</string>
    <key>CFBundleVersion</key><string>1.0</string>
    <key>CFBundleShortVersionString</key><string>1.0</string>
    <key>CFBundleExecutable</key><string>F.R.I.D.A.Y.</string>
    <key>CFBundlePackageType</key><string>APPL</string>
    <key>LSMinimumSystemVersion</key><string>10.15</string>
    <key>NSMicrophoneUsageDescription</key><string>F.R.I.D.A.Y. needs microphone access for voice commands.</string>
    <key>NSPrincipalClass</key><string>NSApplication</string>
</dict>
</plist>
PLIST

echo "  ✓ App bundle created"

echo ""
echo "  [4/4] Creating Desktop shortcut..."
osascript -e "
tell application \"System Events\"
    if not (exists login item \"F.R.I.D.A.Y.\") then
        make login item at end with properties {path:\"$APP_DIR\", hidden:false}
    end if
end tell
" 2>/dev/null || echo "  ⚠ Could not set Login Item"
echo "  ⚠ Login Item skipped (run manually)"

echo ""
echo "  ✓ Desktop shortcut created"

echo ""
echo "  ╔══════════════════════════════════════════════════════════╗"
echo "  ║  ✅ Installation complete!                           ║"
echo "  ║                                                       ║"
echo "  ║  Launch F.R.I.D.A.Y.:                               ║"
echo "  ║    • Click F.R.I.D.A.Y..app on Desktop              ║"
echo "  ║    • Or search Spotlight: F.R.I.D.A.Y.                ║"
echo "  ║                                                       ║"
echo "  ║  It starts automatically on Mac login.                  ║"
echo "  ╚══════════════════════════════════════════════════════════╝"
echo ""

echo "  Run now? (y/n)"
read -r RUN_NOW
if [ "$RUN_NOW" = "y" ] || [ "$RUN_NOW" = "Y" ]; then
    echo "  Starting F.R.I.D.A.Y..."
    open "$APP_DIR"
fi
