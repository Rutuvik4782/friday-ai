#!/bin/bash
# =============================================================================
# F.R.I.D.A.Y. macOS App — Complete Installer
# Creates Desktop shortcut, Login Item, and startup agent
# =============================================================================

set -e

echo ""
echo "  ╔══════════════════════════════════════════════════════════════╗"
echo "  ║       F.R.I.D.A.Y. — Advanced macOS AI Installer         ║"
echo "  ╚══════════════════════════════════════════════════════════════╝"
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$HOME/Applications/F.R.I.D.A.Y..app"
DESKTOP_LINK="$HOME/Desktop/F.R.I.D.A.Y..app"
LAUNCH_AGENT="$HOME/Library/LaunchAgents/com.friday.ai.agent.plist"

echo "  [1/5] Checking Python..."
if ! command -v python3 &>/dev/null; then
    echo "  ✗ Python 3 not found."
    exit 1
fi
echo "  ✓ Python 3 found"

echo ""
echo "  [2/5] Installing Python dependencies..."
python3 -m pip install PyQt6 pyttsx3 sounddevice edge-tts --break-system-packages --quiet 2>/dev/null || \
python3 -m pip install PyQt6 pyttsx3 sounddevice edge-tts --break-system-packages
echo "  ✓ Dependencies installed"

echo ""
echo "  [3/5] Creating F.R.I.D.A.Y. app bundle..."
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"
mkdir -p "$APP_DIR/Contents/Resources/Data"
mkdir -p "$APP_DIR/Contents/Resources/Data/plugins"

cat > "$APP_DIR/Contents/MacOS/F.R.I.D.A.Y." << 'LAUNCHER'
#!/bin/bash
RESOURCES_DIR="$(dirname "$0")/../Resources"
exec python3 "$RESOURCES_DIR/friday_app.py" "$@"
LAUNCHER
chmod +x "$APP_DIR/Contents/MacOS/F.R.I.D.A.Y."

cp "$SCRIPT_DIR/friday_app.py" "$APP_DIR/Contents/Resources/"
cp "$SCRIPT_DIR/voice_helper.swift" "$APP_DIR/Contents/Resources/"

cat > "$APP_DIR/Contents/Info.plist" << 'PLIST'
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
    <key>CFBundleIconFile</key><string></string>
    <key>LSMinimumSystemVersion</key><string>10.15</string>
    <key>NSMicrophoneUsageDescription</key><string>F.R.I.D.A.Y. needs microphone access for voice commands and clap detection.</string>
    <key>NSSpeechRecognitionUsageDescription</key><string>F.R.I.D.A.Y. uses speech recognition to hear your voice commands.</string>
    <key>NSPrincipalClass</key><string>NSApplication</string>
    <key>LSUIElement</key><false/>
    <key>NSHighResolutionCapable</key><true/>
</dict>
</plist>
PLIST

echo "  ✓ App bundle created at $APP_DIR"

echo ""
echo "  [4/5] Setting up Desktop shortcut..."
rm -f "$DESKTOP_LINK"
ln -sf "$APP_DIR" "$DESKTOP_LINK"
echo "  ✓ Desktop shortcut created: F.R.I.D.A.Y..app"

echo ""
echo "  [5/5] Setting up auto-start on Mac boot..."
mkdir -p "$HOME/Library/LaunchAgents"

cat > "$LAUNCH_AGENT" << AGENT
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.friday.ai.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/open</string>
        <string>-a</string>
        <string>F.R.I.D.A.Y.</string>
    </array>
    <key>RunAtLoad</key><true/>
    <key>KeepAlive</key><false/>
    <key>LaunchOnlyOnce</key><true/>
    <key>StartInterval</key><integer>10</integer>
</dict>
</plist>
AGENT

launchctl unload "$LAUNCH_AGENT" 2>/dev/null || true
launchctl load "$LAUNCH_AGENT" 2>/dev/null || true
echo "  ✓ Auto-start on boot enabled"

echo ""
echo "  ╔══════════════════════════════════════════════════════════════╗"
echo "  ║  ✅ F.R.I.D.A.Y. Installation Complete!                ║"
echo "  ║                                                         ║"
echo "  ║  HOW TO LAUNCH:                                        ║"
echo "  ║    1. Double-click F.R.I.D.A.Y..app on Desktop         ║"
echo "  ║    2. Or press Cmd+Space and type 'friday'             ║"
echo "  ║                                                         ║"
echo "  ║  AUTO-START:                                          ║"
echo "  ║    F.R.I.D.A.Y. will launch automatically             ║"
echo "  ║    when you log in to your Mac.                        ║"
echo "  ║                                                         ║"
echo "  ║  WAKE WORD:                                           ║"
echo "  ║    • Clap twice — she activates                       ║"
echo "  ║    • Say 'Wakeup Buddy' — she activates              ║"
echo "  ║                                                         ║"
echo "  ║  VOICE COMMANDS:                                      ║"
echo "  ║    Click the VOICE button, then speak!               ║"
echo "  ╚══════════════════════════════════════════════════════════════╝"
echo ""

echo "  Launch now? (y/n)"
read -r RUN_NOW
if [ "$RUN_NOW" = "y" ] || [ "$RUN_NOW" = "Y" ]; then
    echo "  Starting F.R.I.D.A.Y..."
    open "$APP_DIR"
fi
