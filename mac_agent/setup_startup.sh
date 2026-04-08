#!/bin/bash
# ============================================================
# F.R.I.D.A.Y. — Mac Startup Setup
# ============================================================
# Run this ONCE to make F.R.I.D.A.Y. start when your Mac boots.
# 
# Usage: bash setup_startup.sh
#

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/boot_sequence.py"
PLIST_NAME="com.friday.ai.plist"
PLIST_PATH="$HOME/Library/LaunchAgents/$PLIST_NAME"
APP_NAME="F.R.I.D.A.Y."

echo ""
echo "  ╔══════════════════════════════════════════════╗"
echo "  ║  F.R.I.D.A.Y. — Mac Startup Setup         ║"
echo "  ╚══════════════════════════════════════════════╝"
echo ""

# Ask for user's name
echo "  What's your name? (I'll use it in greetings)"
echo -n "  > "
read -r USER_NAME

# Update the Python script with user's name
sed -i '' "s/YOUR_NAME = \"boss\"/YOUR_NAME = \"$USER_NAME\"/" "$PYTHON_SCRIPT"
echo "  ✓ Name set to: $USER_NAME"

# Create the LaunchAgents directory
mkdir -p "$HOME/Library/LaunchAgents"

# Create the plist file
cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$PLIST_NAME</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$PYTHON_SCRIPT</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>LaunchOnlyOnce</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/friday-boot.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/friday-error.log</string>
</dict>
</plist>
EOF

echo "  ✓ LaunchAgent created"

# Load the LaunchAgent
launchctl load "$PLIST_PATH" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  ✓ Startup item enabled"
else
    echo "  ⚠ Could not auto-load (will work on next restart)"
fi

echo ""
echo "  ╔══════════════════════════════════════════════╗"
echo "  ║  Setup complete!                             ║"
echo "  ║                                              ║"
echo "  ║  F.R.I.D.A.Y. will now greet you            ║"
echo "  ║  every time your Mac starts up.              ║"
echo "  ║                                              ║"
echo "  ║  💡 It will speak a greeting with weather    ║"
echo "  ║     and news, then wait for you.            ║"
echo "  ║                                              ║"
echo "  ║  Test it now: python3 boot_sequence.py       ║"
echo "  ╚══════════════════════════════════════════════╝"
echo ""

# Ask to run now
echo "  Run F.R.I.D.A.Y. now? (y/n)"
echo -n "  > "
read -r RUN_NOW
if [ "$RUN_NOW" = "y" ] || [ "$RUN_NOW" = "Y" ]; then
    echo ""
    echo "  Starting F.R.I.D.A.Y. ..."
    cd "$SCRIPT_DIR" && python3 boot_sequence.py
fi
