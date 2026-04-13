#!/usr/bin/env python3
"""
F.R.I.D.A.Y. — Advanced JARVIS-Style macOS AI Assistant
With natural voice, system control, and intelligent automation.
"""

import sys, os, json, time, threading, datetime, math, random, subprocess, tempfile
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea, QFrame, QGraphicsView,
    QGraphicsScene, QSplashScreen, QLineEdit
)
from PyQt6.QtCore import (
    Qt, QTimer, QPointF, QObject, pyqtSignal
)
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QBrush, QPen, QPolygonF
)

FRIDAY_SERVER = "https://friday-ai-2hbv.onrender.com"
YOUR_NAME = "Rutwik"
LOCATION = "Pune"


# =============================================================================
# VOICE ENGINE — Natural edge-tts voices
# =============================================================================

class FridayVoice:
    def __init__(self):
        self.voice_name = "en-US-GuyNeural"
        self.rate = "+0%"
        self.volume = "+0%"
        self._check_edge_tts()

    def _check_edge_tts(self):
        try:
            import edge_tts
            self._edge_available = True
        except ImportError:
            self._edge_available = False

    def speak(self, text):
        def run():
            try:
                if self._edge_available:
                    self._speak_edge(text)
                else:
                    self._speak_say(text)
            except Exception:
                try:
                    self._speak_say(text)
                except Exception:
                    pass
        threading.Thread(target=run, daemon=True).start()

    def _speak_edge(self, text):
        import edge_tts, asyncio
        async def _talk():
            try:
                mp3_path = tempfile.mktemp(suffix=".mp3")
                communicate = edge_tts.Communicate(text, self.voice_name, rate=self.rate, volume=self.volume)
                await communicate.save(mp3_path)
                subprocess.run(["afplay", mp3_path], timeout=30, capture_output=True)
                os.unlink(mp3_path)
            except Exception:
                self._speak_say(text)

        try:
            asyncio.run(_talk())
        except Exception:
            self._speak_say(text)

    def _speak_say(self, text):
        cmd = ["say", "-v", "Samantha", "-r", "165", text]
        subprocess.run(cmd, timeout=30, capture_output=True)


# =============================================================================
# SYSTEM CONTROLLER — Full laptop automation
# =============================================================================

class SystemController:
    def __init__(self):
        self.last_screenshot = None

    def execute(self, command):
        command = command.lower().strip()
        if "volume" in command:
            return self._volume(command)
        elif "brightness" in command:
            return self._brightness(command)
        elif "open" in command or "launch" in command:
            return self._open_app(command)
        elif "close" in command:
            return self._close_app(command)
        elif "screenshot" in command or "screen shot" in command:
            return self._screenshot()
        elif "search" in command and "web" in command:
            return self._search_web(command)
        elif "play" in command and ("music" in command or "song" in command):
            return self._music_control("play")
        elif "pause" in command:
            return self._music_control("pause")
        elif "next" in command or "skip" in command:
            return self._music_control("next")
        elif "previous" in command or "back" in command:
            return self._music_control("previous")
        elif "notification" in command or "notify" in command:
            return self._notification(command)
        elif "system" in command and "info" in command:
            return self._system_info()
        elif "battery" in command:
            return self._battery()
        elif "wifi" in command:
            return self._wifi()
        elif "empty" in command and "trash" in command:
            return self._empty_trash()
        elif "sleep" in command:
            return self._sleep()
        elif "restart" in command or "reboot" in command:
            return self._restart()
        elif "shutdown" in command:
            return self._shutdown()
        elif "read" in command and "clipboard" in command:
            return self._read_clipboard()
        elif "copy" in command:
            return self._copy_to_clipboard(command)
        elif "lock" in command:
            return self._lock_screen()
        elif "hide" in command:
            return self._hide_apps()
        else:
            return self._run_terminal(command)

    def _volume(self, command):
        if "mute" in command or "silent" in command:
            subprocess.run(["osascript", "-e", "set volume output volume 0"])
            return "Volume muted."
        if "max" in command or "maximum" in command:
            subprocess.run(["osascript", "-e", "set volume output volume 100"])
            return "Volume set to maximum."
        nums = [int(s) for s in command.split() if s.isdigit()]
        if nums:
            vol = max(0, min(100, nums[0]))
            subprocess.run(["osascript", "-e", f"set volume output volume {vol}"])
            return f"Volume set to {vol}%."
        result = subprocess.run(
            ["osascript", "-e", "output volume of (get volume settings)"],
            capture_output=True, text=True
        )
        vol = result.stdout.strip()
        return f"Current volume is {vol}%."

    def _brightness(self, command):
        try:
            nums = [int(s) for s in command.split() if s.isdigit()]
            if nums:
                brightness = max(0, min(100, nums[0]))
                subprocess.run(["brightness", str(brightness / 100)], capture_output=True)
                return f"Brightness set to {brightness}%."
            result = subprocess.run(
                ["brightness", "-l"], capture_output=True, text=True
            )
            for line in result.stdout.split("\n"):
                if "brightness" in line.lower():
                    val = float(line.split(":")[-1].strip())
                    return f"Current brightness is {int(val * 100)}%."
            return "Could not read brightness."
        except FileNotFoundError:
            return "Brightness control requires brightness CLI. Install via: brew install brightness"
        except Exception as e:
            return f"Error: {e}"

    def _open_app(self, command):
        apps = {
            "chrome": "Google Chrome",
            "safari": "Safari",
            "firefox": "Firefox",
            "terminal": "Terminal",
            "finder": "Finder",
            "spotify": "Spotify",
            "music": "Music",
            "notes": "Notes",
            "calendar": "Calendar",
            "mail": "Mail",
            "messages": "Messages",
            "discord": "Discord",
            "slack": "Slack",
            "xcode": "Xcode",
            "vscode": "Visual Studio Code",
            "code": "Visual Studio Code",
            "pycharm": "PyCharm",
            "sublime": "Sublime Text",
            "notion": "Notion",
            "whatsapp": "WhatsApp",
            "telegram": "Telegram",
            "zoom": "Zoom",
            "teams": "Microsoft Teams",
            "settings": "System Preferences",
            "activity": "Activity Monitor",
            "photos": "Photos",
            "app store": "App Store",
            "calculator": "Calculator",
            "reminders": "Reminders",
        }
        for keyword, app_name in apps.items():
            if keyword in command:
                subprocess.run(["open", "-a", app_name], capture_output=True)
                return f"Opening {app_name}."
        return "App not recognized. Try: open Chrome, Safari, Terminal, Finder, Spotify, etc."

    def _close_app(self, command):
        apps = {
            "chrome": "Google Chrome",
            "safari": "Safari",
            "terminal": "Terminal",
            "spotify": "Spotify",
        }
        for keyword, app_name in apps.items():
            if keyword in command:
                subprocess.run(["osascript", "-e", f'tell application "{app_name}" to quit'], capture_output=True)
                return f"Closing {app_name}."
        return "Which app should I close?"

    def _screenshot(self):
        path = os.path.expanduser(f"~/Desktop/screenshot_{int(time.time())}.png")
        subprocess.run(["screencapture", "-x", path], capture_output=True)
        self.last_screenshot = path
        return f"Screenshot saved to Desktop."

    def _search_web(self, command):
        query = command.replace("search the web for", "").replace("search", "").replace("web", "").strip()
        if query:
            url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}"
            subprocess.run(["open", url], capture_output=True)
            return f"Searching for: {query}"
        return "What should I search for?"

    def _music_control(self, action):
        try:
            if action == "play":
                subprocess.run(["osascript", "-e", "tell application \"Spotify\" to play"], capture_output=True)
                return "Playing music."
            elif action == "pause":
                subprocess.run(["osascript", "-e", "tell application \"Spotify\" to pause"], capture_output=True)
                return "Pausing music."
            elif action == "next":
                subprocess.run(["osascript", "-e", "tell application \"Spotify\" to next track"], capture_output=True)
                return "Next track."
            elif action == "previous":
                subprocess.run(["osascript", "-e", "tell application \"Spotify\" to previous track"], capture_output=True)
                return "Previous track."
        except Exception:
            return "Music control requires Spotify to be open."

    def _notification(self, command):
        msg = command.replace("notification", "").replace("notify", "").strip()
        if msg:
            subprocess.run(
                ["osascript", "-e", f'display notification "{msg}" with title "F.R.I.D.A.Y."'],
                capture_output=True
            )
            return f"Notification sent: {msg}"
        return "What should the notification say?"

    def _system_info(self):
        result = subprocess.run(
            ["sysctl", "hw.model", "hw.memsize", "hw.ncpu"],
            capture_output=True, text=True
        )
        info = result.stdout
        uptime = subprocess.run(["uptime"], capture_output=True, text=True).stdout.strip()
        return f"System: {info}\nUptime: {uptime}"

    def _battery(self):
        result = subprocess.run(
            ["pmset", "-g", "batt"],
            capture_output=True, text=True
        )
        return result.stdout.strip() or "Could not read battery status."

    def _wifi(self):
        result = subprocess.run(
            ["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-I"],
            capture_output=True, text=True
        )
        for line in result.stdout.split("\n"):
            if "SSID" in line:
                ssid = line.split(":")[-1].strip()
                return f"Connected to WiFi: {ssid}"
        return "WiFi status unknown."

    def _empty_trash(self):
        subprocess.run(["osascript", "-e", 'tell application "Finder" to empty trash'], capture_output=True)
        return "Trash emptied."

    def _sleep(self):
        subprocess.run(["pmset", "sleepnow"], capture_output=True)
        return "Putting Mac to sleep."

    def _restart(self):
        subprocess.run(["osascript", "-e", 'tell application "System Events" to restart'], capture_output=True)
        return "Restarting Mac."

    def _shutdown(self):
        subprocess.run(["osascript", "-e", 'tell application "System Events" to shut down'], capture_output=True)
        return "Shutting down Mac."

    def _read_clipboard(self):
        result = subprocess.run(["pbpaste"], capture_output=True, text=True)
        return f"Clipboard: {result.stdout.strip()[:200]}" or "Clipboard is empty."

    def _copy_to_clipboard(self, command):
        text = command.replace("copy", "").strip()
        if text:
            subprocess.run(["pbcopy"], input=text, text=True)
            return f"Copied to clipboard: {text[:50]}."
        return "What should I copy?"

    def _lock_screen(self):
        subprocess.run(["/System/Library/CoreServices/Menu\\ Extras/User.menu/Contents/Resources/CGSession", "-suspend"], capture_output=True)
        return "Mac locked."

    def _hide_apps(self):
        subprocess.run(["osascript", "-e", 'tell application "System Events" to set visible of every process to false'], capture_output=True)
        return "All apps hidden."

    def _run_terminal(self, command):
        if command.startswith("run ") or command.startswith("execute ") or command.startswith("$"):
            cmd = command.replace("run ", "").replace("execute ", "").replace("$", "").strip()
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                out = result.stdout.strip() or result.stderr.strip() or "Command executed."
                return out[:500]
            except Exception as e:
                return f"Error: {e}"
        return None


# =============================================================================
# WAKE WORD LISTENER — Clap detection + wake word detection
# =============================================================================

class WakeWordListener(QObject):
    triggered = pyqtSignal()
    status = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running = False
        self._thread = None
        self._audio_available = self._check_audio()

    def _check_audio(self):
        try:
            import sounddevice as sd
            sd.check_input_settings()
            return True
        except Exception:
            pass
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            p.terminate()
            return True
        except Exception:
            pass
        return False

    def start(self):
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        self.status.emit("active")

    def stop(self):
        self.running = False

    def _listen_loop(self):
        try:
            import sounddevice as sd
            self._listen_sounddevice()
        except ImportError:
            try:
                self._listen_pyaudio()
            except ImportError:
                self._listen_swift_loop()

    def _listen_sounddevice(self):
        import sounddevice as sd
        import numpy as np

        clap_times = []
        wake_word_times = []

        def callback(indata, frames, time_info, status):
            nonlocal clap_times, wake_word_times
            if status:
                return
            audio_data = np.abs(indata[:, 0])
            rms = np.sqrt(np.mean(audio_data ** 2))
            amplitude = rms * 100

            now = time.time()

            if amplitude > 30:
                if not clap_times or (now - clap_times[-1]) > 0.3:
                    clap_times.append(now)

                if len(clap_times) >= 2:
                    if clap_times[-1] - clap_times[-2] < 1.5:
                        if self.running:
                            self.triggered.emit()
                            time.sleep(2)

                clap_times = [t for t in clap_times if now - t < 2]

        try:
            with sd.InputStream(
                channels=1, samplerate=16000, blocksize=1024,
                callback=callback, dtype='float32'
            ):
                while self.running:
                    time.sleep(0.1)
        except Exception:
            pass

    def _listen_pyaudio(self):
        import pyaudio
        import numpy as np

        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paFloat32, channels=1,
                        rate=16000, input=True, frames_per_buffer=1024)
        clap_times = []
        now = time.time()

        try:
            while self.running:
                data = np.frombuffer(stream.read(1024), dtype=np.float32)
                rms = np.sqrt(np.mean(data ** 2))
                amplitude = rms * 100

                if amplitude > 30:
                    if not clap_times or (time.time() - clap_times[-1]) > 0.3:
                        clap_times.append(time.time())

                    if len(clap_times) >= 2:
                        if clap_times[-1] - clap_times[-2] < 1.5:
                            if self.running:
                                self.triggered.emit()
                                time.sleep(2)
                    clap_times = [t for t in clap_times if time.time() - t < 2]

                time.sleep(0.01)
        except Exception:
            pass
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

    def _listen_swift_loop(self):
        import subprocess, os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        swift_path = os.path.join(script_dir, "voice_helper.swift")

        while self.running:
            try:
                proc = subprocess.Popen(
                    ["swift", swift_path],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                out, _ = proc.communicate(timeout=8)
                for line in out.split("\n"):
                    if line.startswith("TEXT:"):
                        text = line[5:].lower().strip()
                        if any(w in text for w in ["wakeup buddy", "hey buddy", "hey friday", "wake up buddy"]):
                            if self.running:
                                self.triggered.emit()
                                time.sleep(2)
            except Exception:
                pass
            time.sleep(0.5)


class ArcReactorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(260, 260)
        self.angle = 0.0
        self.phase = 0.0
        self.pulse = 0.5
        self.wake_active = False
        self.wake_timer = 0
        self.particles = []
        for _ in range(20):
            self.particles.append({
                'angle': random.random() * 360,
                'radius': 40 + random.random() * 80,
                'speed': 0.2 + random.random() * 0.5,
                'size': 1 + random.random() * 2,
                'alpha': 50 + random.random() * 100
            })
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)

    def animate(self):
        self.angle += 1
        self.phase += 0.04
        self.pulse = 0.6 + 0.4 * math.sin(self.phase * 1.5)
        if self.wake_active:
            self.wake_timer += 1
            if self.wake_timer > 60:
                self.wake_active = False
                self.wake_timer = 0
        for p in self.particles:
            p['angle'] += p['speed']
        self.update()

    def pulse_wake(self):
        self.wake_active = True
        self.wake_timer = 0

    def paintEvent(self, event):
        w = min(self.width(), self.height())
        cx, cy = self.width() / 2, self.height() / 2
        s = w / 2
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        p.translate(cx, cy)
        p.scale(s / 130, s / 130)

        base_color = QColor(0, 180, 255) if not self.wake_active else QColor(0, 255, 180)
        glow_intensity = int(200 * self.pulse)

        # Outer ambient glow
        for i in range(12, 0, -1):
            alpha = int(3 * (13 - i))
            radius = 125 + i * 4
            p.setPen(QPen(QColor(base_color.red(), base_color.green(), base_color.blue(), alpha), i * 2))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(-radius, -radius, radius * 2, radius * 2)

        # Containment ring (outermost)
        p.setPen(QPen(QColor(30, 40, 50), 4))
        p.setBrush(QBrush(QColor(15, 20, 28)))
        p.drawEllipse(-125, -125, 250, 250)

        # Outer ring with tick marks
        for i in range(60):
            angle_rad = math.radians(i * 6)
            inner_r = 118
            outer_r = 122 if i % 5 == 0 else 120
            x1 = inner_r * math.cos(angle_rad)
            y1 = inner_r * math.sin(angle_rad)
            x2 = outer_r * math.cos(angle_rad)
            y2 = outer_r * math.sin(angle_rad)
            if i % 5 == 0:
                p.setPen(QPen(QColor(0, 140, 220, 180), 2))
            else:
                p.setPen(QPen(QColor(0, 100, 160, 80), 1))
            p.drawLine(int(x1), int(y1), int(x2), int(y2))

        # Energy ring 1 (slow, clockwise)
        r1_angle = self.angle * 0.3
        for i in range(6):
            seg_angle = math.radians(r1_angle + i * 60)
            sx = 105 * math.cos(seg_angle)
            sy = 105 * math.sin(seg_angle)
            ex = 118 * math.cos(seg_angle)
            ey = 118 * math.sin(seg_angle)
            p.setPen(QPen(QColor(0, glow_intensity, glow_intensity, 220), 3))
            p.drawLine(int(sx), int(sy), int(ex), int(ey))

        # Energy ring 2 (medium, counter-clockwise)
        r2_angle = -self.angle * 0.5
        for i in range(4):
            seg_angle = math.radians(r2_angle + i * 90 + 45)
            sx = 88 * math.cos(seg_angle)
            sy = 88 * math.sin(seg_angle)
            ex = 98 * math.cos(seg_angle)
            ey = 98 * math.sin(seg_angle)
            p.setPen(QPen(QColor(0, glow_intensity + 20, glow_intensity + 20, 200), 2))
            p.drawLine(int(sx), int(sy), int(ex), int(ey))

        # Inner rotating ring (fast, clockwise)
        r3_angle = self.angle * 0.8
        for i in range(8):
            seg_angle = math.radians(r3_angle + i * 45)
            sx = 68 * math.cos(seg_angle)
            sy = 68 * math.sin(seg_angle)
            ex = 78 * math.cos(seg_angle)
            ey = 78 * math.sin(seg_angle)
            p.setPen(QPen(QColor(0, glow_intensity + 40, glow_intensity + 40, 180), 2))
            p.drawLine(int(sx), int(sy), int(ex), int(ey))

        # Hexagonal housing
        hex_path = QPainterPath()
        for i in range(6):
            angle_rad = math.radians(60 * i - 30)
            x = 62 * math.cos(angle_rad)
            y = 62 * math.sin(angle_rad)
            if i == 0:
                hex_path.moveTo(x, y)
            else:
                hex_path.lineTo(x, y)
        hex_path.closeSubpath()
        hex_pen = QPen(QColor(0, 140, 200, 150), 2)
        p.setPen(hex_pen)
        p.setBrush(QBrush(QColor(5, 15, 25, 100)))
        p.drawPath(hex_path)

        # Inner hex detail
        inner_hex = QPainterPath()
        for i in range(6):
            angle_rad = math.radians(-self.angle * 0.2 + 60 * i - 30)
            x = 42 * math.cos(angle_rad)
            y = 42 * math.sin(angle_rad)
            if i == 0:
                inner_hex.moveTo(x, y)
            else:
                inner_hex.lineTo(x, y)
        inner_hex.closeSubpath()
        p.setPen(QPen(QColor(0, 160, 220, 120), 1))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(inner_hex)

        # Arc segments (energy arcs)
        arc_angle = self.angle * 1.2
        for i in range(4):
            span = 25
            start_a = math.radians(arc_angle + i * 90)
            path = QPainterPath()
            path.moveTo(0, 0)
            for j in range(span + 1):
                a = start_a + math.radians(j)
                path.lineTo(55 * math.cos(a), 55 * math.sin(a))
            path.lineTo(0, 0)
            arc_alpha = int(60 + 40 * math.sin(self.phase + i * 1.5))
            p.setPen(QPen(QColor(0, 200, 255, arc_alpha), 2))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawPath(path)

        # Core glow layers
        core_r = 28 * (0.85 + 0.15 * self.pulse)
        for i in range(8, 0, -1):
            glow_r = core_r + i * 4
            alpha = int(12 * (9 - i) * self.pulse)
            p.setPen(QPen(QColor(base_color.red(), base_color.green(), base_color.blue(), alpha)))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(int(-glow_r), int(-glow_r), int(glow_r * 2), int(glow_r * 2))

        # Core body (dark metallic)
        core_grad = QRadialGradient(0, 0, core_r)
        core_grad.setColorAt(0, QColor(200, 240, 255, 255))
        core_grad.setColorAt(0.4, QColor(0, 160, 230, 255))
        core_grad.setColorAt(0.8, QColor(0, 80, 140, 200))
        core_grad.setColorAt(1.0, QColor(0, 30, 60, 150))
        p.setPen(QPen(QColor(0, 100, 160, 200), 2))
        p.setBrush(QBrush(core_grad))
        p.drawEllipse(int(-core_r), int(-core_r), int(core_r * 2), int(core_r * 2))

        # Core highlight
        highlight_r = core_r * 0.4
        hl_grad = QRadialGradient(-core_r * 0.2, -core_r * 0.2, highlight_r)
        hl_grad.setColorAt(0, QColor(255, 255, 255, 200))
        hl_grad.setColorAt(0.5, QColor(200, 240, 255, 100))
        hl_grad.setColorAt(1.0, QColor(100, 200, 255, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(hl_grad))
        p.drawEllipse(int(-highlight_r), int(-highlight_r), int(highlight_r * 2), int(highlight_r * 2))

        # Particles
        for particle in self.particles:
            dist = particle['radius'] * (0.6 + 0.4 * self.pulse)
            px = dist * math.cos(math.radians(particle['angle']))
            py = dist * math.sin(math.radians(particle['angle']))
            alpha = int(particle['alpha'] * self.pulse)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(QColor(0, 200, 255, alpha)))
            p.drawEllipse(int(px - particle['size']), int(py - particle['size']), int(particle['size'] * 2), int(particle['size'] * 2))

        # Reflection on bottom
        refl_path = QPainterPath()
        refl_path.moveTo(-110, 120)
        refl_path.lineTo(110, 120)
        refl_path.lineTo(90, 125)
        refl_path.lineTo(-90, 125)
        refl_path.closeSubpath()
        refl_grad = QLinearGradient(0, 120, 0, 128)
        refl_grad.setColorAt(0, QColor(0, 150, 220, 60))
        refl_grad.setColorAt(1, QColor(0, 80, 140, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(refl_grad))
        p.drawPath(refl_path)

        # Metallic rim highlight (top)
        rim_path = QPainterPath()
        rim_path.moveTo(-120, -122)
        rim_path.arcTo(-122, -124, 244, 8, 200, 40)
        rim_grad = QLinearGradient(-120, -125, -120, -118)
        rim_grad.setColorAt(0, QColor(80, 120, 160, 100))
        rim_grad.setColorAt(0.5, QColor(40, 80, 120, 60))
        rim_grad.setColorAt(1, QColor(20, 40, 60, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(rim_grad))
        p.drawPath(rim_path)


class ArcReactorWidgetOLD(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setSceneRect(-200, -200, 400, 400)
        self.setBackgroundRole(QPalette.ColorRole.NoRole)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.angle = 0
        self.pulse = 0.0
        self.phase = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(16)
        self.build_reactor()

    def build_reactor(self):
        self.scene.clear()
        no_pen = QPen()
        no_pen.setStyle(Qt.PenStyle.NoPen)
        no_brush = QBrush()
        self.rings = []

        outer_glow = self.scene.addEllipse(-180, -180, 360, 360)
        outer_glow.setPen(no_pen)
        outer_glow.setBrush(no_brush)
        self.outer_glow = outer_glow

        for i in range(6):
            radius = 140 - i * 15
            ring = self.scene.addEllipse(-radius, -radius, radius*2, radius*2)
            speeds = [1.2, -0.9, 1.5, -1.1, 0.8, -1.4]
            ring.setPen(QPen(QColor(0, 180 + i*8, 255), 1))
            ring.setBrush(no_brush)
            self.rings.append((ring, speeds[i]))

        self.hex_ring = self.scene.addPolygon(self.hexagon(60))
        hex_pen = QPen(QColor(0, 210, 255, 180), 2)
        self.hex_ring.setPen(hex_pen)
        self.hex_ring.setBrush(no_brush)

        self.arcs = []
        for i in range(12):
            arc = self.scene.addEllipse(-75, -75, 150, 150)
            arc.setPen(QPen(QColor(0, 230, 255, 80), 1))
            arc.setBrush(no_brush)
            self.arcs.append(arc)

        self.inner_hex = self.scene.addPolygon(self.hexagon(35))
        ih_pen = QPen(QColor(0, 180, 255, 120), 1)
        self.inner_hex.setPen(ih_pen)
        self.inner_hex.setBrush(no_brush)

        self.core_glow = self.scene.addEllipse(-25, -25, 50, 50)
        self.core_glow.setPen(no_pen)
        self.core_glow.setBrush(QBrush(QColor(0, 180, 255, 60)))

        self.core = self.scene.addEllipse(-14, -14, 28, 28)
        self.core.setPen(no_pen)
        self.core.setBrush(QBrush(QColor(200, 240, 255)))

        self.core_inner = self.scene.addEllipse(-7, -7, 14, 14)
        self.core_inner.setPen(no_pen)
        self.core_inner.setBrush(QBrush(QColor(255, 255, 255)))

    def hexagon(self, size):
        points = []
        for i in range(6):
            angle = math.radians(60 * i - 30)
            points.append(QPointF(size * math.cos(angle), size * math.sin(angle)))
        return QPolygonF(points)

    def tick(self):
        self.angle += 1
        self.phase += 0.03
        self.pulse = 0.5 + 0.5 * math.sin(self.phase * 2)

        for i, (ring, speed) in enumerate(self.rings):
            offset = math.sin(self.phase + i * 0.5) * 3
            ring.setRotation(self.angle * speed + offset)

        for i, arc in enumerate(self.arcs):
            arc_angle = self.angle * (1.5 if i % 2 == 0 else -1.2) + i * 30
            arc.setRotation(arc_angle)

        hex_rot = self.angle * 0.3
        self.hex_ring.setRotation(hex_rot)
        self.inner_hex.setRotation(-hex_rot * 1.5)

        core_scale = 0.7 + self.pulse * 0.5
        self.core.setScale(core_scale)
        self.core_inner.setScale(core_scale * 0.8)

        glow_alpha = int(30 + self.pulse * 40)
        self.core_glow.setBrush(QBrush(QColor(0, 180, 255, glow_alpha)))
        glow_scale = 0.8 + self.pulse * 0.4
        self.core_glow.setScale(glow_scale)

        self.scene.update()

    def pulse_wake(self):
        self.phase = 0
        self.pulse = 1.0
        for ring, speed in self.rings:
            ring.setPen(QPen(QColor(0, 255, 200), 3))
        self.scene.update()
        QTimer.singleShot(2000, self._reset_wake)

    def _reset_wake(self):
        ring_configs = [
            (140, 1.2, QColor(0, 180, 255)),
            (125, -0.9, QColor(0, 188, 255)),
            (110, 1.5, QColor(0, 196, 255)),
            (95, -1.1, QColor(0, 204, 255)),
            (80, 0.8, QColor(0, 212, 255)),
            (65, -1.4, QColor(0, 220, 255)),
        ]
        for i, (ring, speed) in enumerate(self.rings):
            ring.setPen(QPen(ring_configs[i][2], 1))
        self.scene.update()


class VoiceListener(QObject):
    heard = pyqtSignal(str)
    status_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.is_listening = False
        self._proc = None
        self.status_changed.emit("ready")

    def start(self):
        if self.is_listening:
            self.stop()
            return
        self.is_listening = True
        self.status_changed.emit("listening")
        threading.Thread(target=self._run_swift, daemon=True).start()

    def _run_swift(self):
        import subprocess, os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        swift_path = os.path.join(script_dir, "voice_helper.swift")
        if not os.path.exists(swift_path):
            self.heard.emit("")
            self.status_changed.emit("unavailable")
            self.is_listening = False
            return
        try:
            self._proc = subprocess.Popen(
                ["swift", swift_path],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            out, _ = self._proc.communicate(timeout=12)
            for line in out.split("\n"):
                if line.startswith("TEXT:"):
                    text = line[5:].strip()
                    if text:
                        self.heard.emit(text)
                        break
        except subprocess.TimeoutExpired:
            if self._proc:
                self._proc.kill()
        except FileNotFoundError:
            self.heard.emit("")
            self.status_changed.emit("unavailable")
        except Exception:
            pass
        finally:
            self.is_listening = False
            self.status_changed.emit("idle")

    def stop(self):
        self.is_listening = False
        if self._proc:
            try:
                self._proc.kill()
            except Exception:
                pass


class ChatBubble(QFrame):
    def __init__(self, text, is_user=False, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: {'rgba(0, 40, 80, 0.85)' if not is_user else 'rgba(80, 30, 0, 0.85)'};
                border: 1px solid {'rgba(0, 180, 255, 0.3)' if not is_user else 'rgba(255, 120, 0, 0.3)'};
                border-radius: 10px;
                padding: 10px;
                margin: 4px 20px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        label = QLabel(text)
        label.setWordWrap(True)
        label.setStyleSheet("color: #c8e8f0; background: transparent; border: none;")
        label.setFont(QFont("Rajdhani", 13))
        layout.addWidget(label)


class FridayWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.voice = FridayVoice()
        self.voice_input = VoiceListener()
        self.voice_input.heard.connect(self.on_voice_heard)
        self.voice_input.status_changed.connect(self.on_voice_status)
        self.system = SystemController()
        self.wake_word = WakeWordListener()
        self.wake_word.triggered.connect(self.on_wake_triggered)
        self.wake_word.status.connect(self.on_wake_status)
        self.conversation = []
        self._init_ui()
        self.greeting()
        self.wake_word.start()

    def _init_ui(self):
        self.setWindowTitle("F.R.I.D.A.Y. — Tony Stark AI Assistant")
        self.setStyleSheet("background-color: #030810;")
        self.resize(1000, 750)
        self.setMinimumSize(800, 600)

        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )

        title = QLabel("  F.R.I.D.A.Y.  —  FULLY RESPONSIVE INTELLIGENT DIGITAL ASSISTANT FOR YOU")
        title.setStyleSheet("""
            background: rgba(0, 15, 35, 0.95);
            color: #00d4ff;
            font-family: Arial;
            font-size: 12px;
            font-weight: bold;
            letter-spacing: 2px;
            padding: 8px 15px;
            border-bottom: 1px solid rgba(0, 212, 255, 0.2);
        """)
        title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        title.setFixedHeight(36)

        central = QWidget()
        self.setCentralWidget(central)
        main = QVBoxLayout(central)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)
        main.addWidget(title)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(10, 10, 10, 10)

        top_row = QHBoxLayout()

        self.arc = ArcReactorWidget()
        self.arc.setFixedSize(260, 260)
        top_row.addWidget(self.arc)

        status_panel = QWidget()
        status_panel.setStyleSheet("""
            background: rgba(0, 15, 35, 0.8);
            border: 1px solid rgba(0, 212, 255, 0.15);
            border-radius: 8px;
            padding: 5px;
        """)
        sp_layout = QVBoxLayout(status_panel)
        sp_layout.setContentsMargins(10, 10, 10, 10)
        sp_layout.setSpacing(8)

        self.status_label = QLabel("STATUS: ONLINE")
        self.status_label.setStyleSheet("color: #00ff88; font-size: 13px; font-weight: bold; letter-spacing: 2px;")
        self.status_label.setFont(QFont("Courier", 12, QFont.Weight.Bold))

        self.time_label = QLabel()
        self.time_label.setStyleSheet("color: rgba(0, 200, 255, 0.7); font-size: 11px;")
        self.time_label.setFont(QFont("Courier", 10))

        self.weather_label = QLabel("WEATHER: Loading...")
        self.weather_label.setStyleSheet("color: rgba(0, 200, 255, 0.7); font-size: 11px;")
        self.weather_label.setFont(QFont("Courier", 10))

        self.response_label = QLabel("RESPONSE: --ms")
        self.response_label.setStyleSheet("color: rgba(0, 200, 255, 0.7); font-size: 11px;")
        self.response_label.setFont(QFont("Courier", 10))

        self.voice_label = QLabel("VOICE: READY")
        self.voice_label.setStyleSheet("color: rgba(0, 212, 255, 0.7); font-size: 11px;")
        self.voice_label.setFont(QFont("Courier", 10))

        self.wake_label = QLabel("WAKE: CLAP 2x or say WAKEUP BUDDY")
        self.wake_label.setStyleSheet("color: rgba(0, 255, 136, 0.7); font-size: 10px;")
        self.wake_label.setFont(QFont("Courier", 9))

        sp_layout.addWidget(self.status_label)
        sp_layout.addWidget(self.time_label)
        sp_layout.addWidget(self.weather_label)
        sp_layout.addWidget(self.response_label)
        sp_layout.addWidget(self.voice_label)
        sp_layout.addWidget(self.wake_label)
        sp_layout.addStretch()
        top_row.addWidget(status_panel, 1)

        actions_panel = QWidget()
        actions_panel.setStyleSheet("""
            background: rgba(0, 15, 35, 0.8);
            border: 1px solid rgba(0, 212, 255, 0.15);
            border-radius: 8px;
            padding: 5px;
        """)
        ap_layout = QVBoxLayout(actions_panel)
        ap_layout.setContentsMargins(10, 10, 10, 10)
        ap_layout.setSpacing(6)

        ap_title = QLabel("QUICK ACTIONS")
        ap_title.setStyleSheet("color: rgba(0, 212, 255, 0.5); font-size: 10px; letter-spacing: 2px;")
        ap_title.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        ap_layout.addWidget(ap_title)

        for name, prompt in [
            ("Weather", "What is the weather in Pune?"),
            ("News", "What are the latest tech news?"),
            ("Code", "Write a Python function to find prime numbers"),
            ("Search", "Search for latest AI developments"),
            ("Translate", "Translate hello to Japanese"),
        ]:
            btn = QPushButton(name)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(0, 30, 60, 0.6);
                    border: 1px solid rgba(0, 212, 255, 0.1);
                    border-radius: 5px;
                    color: #c8e8f0;
                    padding: 6px 12px;
                    text-align: left;
                    font-size: 12px;
                    font-family: Rajdhani;
                }
                QPushButton:hover {
                    background: rgba(0, 60, 120, 0.7);
                    border-color: rgba(0, 212, 255, 0.4);
                }
            """)
            btn.setFont(QFont("Rajdhani", 12))
            btn.clicked.connect(lambda checked, p=prompt: self.send_message(p))
            ap_layout.addWidget(btn)

        top_row.addWidget(actions_panel)
        content_layout.addLayout(top_row)

        self.chat_area = QScrollArea()
        self.chat_area.setStyleSheet("""
            QScrollArea { background: rgba(0, 10, 25, 0.5); border: 1px solid rgba(0, 212, 255, 0.1); border-radius: 8px; }
            QScrollBar:vertical { background: rgba(0, 50, 80, 0.5); width: 4px; border-radius: 2px; }
            QScrollBar::handle { background: rgba(0, 170, 255, 0.5); border-radius: 2px; }
        """)
        self.chat_area.setWidgetResizable(True)
        self.chat_area.setFrameShape(QFrame.Shape.NoFrame)

        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setContentsMargins(10, 10, 10, 10)
        self.chat_layout.setSpacing(8)
        self.chat_layout.addStretch()

        self.chat_area.setWidget(self.chat_container)
        content_layout.addWidget(self.chat_area, 1)

        input_row = QHBoxLayout()

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("  Talk to F.R.I.D.A.Y...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background: rgba(0, 30, 60, 0.7);
                color: #c8e8f0;
                border: 1px solid rgba(0, 212, 255, 0.2);
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                font-family: Rajdhani;
            }
            QLineEdit:focus {
                border: 1px solid #00d4ff;
                background: rgba(0, 50, 100, 0.7);
            }
        """)
        self.input_field.setFont(QFont("Rajdhani", 14))
        self.input_field.returnPressed.connect(self.send_message)

        self.mic_btn = QPushButton("VOICE")
        self.mic_btn.setFixedSize(70, 46)
        self.mic_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 30, 60, 0.7);
                border: 1px solid rgba(0, 212, 255, 0.2);
                border-radius: 8px;
                color: #00d4ff;
                font-weight: bold;
                font-size: 11px;
                letter-spacing: 1px;
            }
            QPushButton:hover { background: rgba(0, 60, 120, 0.7); border-color: #00d4ff; }
            QPushButton.recording {
                background: rgba(255, 50, 0, 0.7);
                border: 1px solid #ff6600;
                color: white;
                animation: pulse 1s ease-in-out infinite;
            }
            @keyframes pulse {
                0%, 100% { box-shadow: 0 0 5px rgba(255, 100, 0, 0.5); }
                50% { box-shadow: 0 0 20px rgba(255, 100, 0, 0.8); }
            }
        """)
        self.mic_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.mic_btn.clicked.connect(self.toggle_voice)

        self.send_btn = QPushButton("SEND")
        self.send_btn.setFixedSize(80, 46)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background: linear-gradient(135deg, #0066aa, #0099dd);
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                letter-spacing: 2px;
            }
            QPushButton:hover { background: linear-gradient(135deg, #0088cc, #00bbff); }
        """)
        self.send_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.send_btn.clicked.connect(self.send_message)

        input_row.addWidget(self.input_field)
        input_row.addWidget(self.mic_btn)
        input_row.addWidget(self.send_btn)
        content_layout.addLayout(input_row)

        main.addWidget(content)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()
        self.show()

    def update_time(self):
        now = datetime.datetime.now()
        self.time_label.setText(
            f"TIME: {now.strftime('%I:%M:%S %p')}\n"
            f"DATE: {now.strftime('%d %b %Y')}"
        )

    def fetch_weather(self):
        try:
            import urllib.request
            url = f"https://wttr.in/{LOCATION}?format=j1"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as r:
                data = json.loads(r.read())
            current = data.get("current_condition", [{}])[0]
            temp = current.get("temp_C", "?")
            condition = current.get("weatherDesc", [{}])[0].get("value", "Clear")
            self.weather_label.setText(f"WEATHER: {temp}C, {condition}\nLOCATION: {LOCATION}")
        except Exception:
            self.weather_label.setText(f"WEATHER: 24C, Clear\nLOCATION: {LOCATION}")

    def greeting(self):
        self.fetch_weather()
        hour = datetime.datetime.now().hour
        if 5 <= hour < 12:
            time_greet = f"Good morning, {YOUR_NAME}."
        elif 12 <= hour < 17:
            time_greet = f"Good afternoon, {YOUR_NAME}."
        elif 17 <= hour < 21:
            time_greet = f"Good evening, {YOUR_NAME}."
        else:
            time_greet = f"Hello there, {YOUR_NAME}. It's late — everything okay?"

        full = (
            f"{time_greet} I am F.R.I.D.A.Y. — Fully Responsive Intelligent Digital Assistant For You. "
            f"I am fully operational and ready to assist you with anything you need. "
            f"From controlling your Mac — opening apps, adjusting volume, taking screenshots — "
            f"to answering questions, writing code, searching the web, and beyond. "
            f"Simply say 'Wakeup Buddy' or clap twice to activate me anytime. "
            f"All systems are online. How may I assist you today?"
        )
        self.add_message(full, False)
        self.voice.speak(full)

    def add_message(self, text, is_user):
        bubble = ChatBubble(text, is_user)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble)
        QTimer.singleShot(50, lambda: self.chat_area.verticalScrollBar().setValue(
            self.chat_area.verticalScrollBar().maximum()
        ))

    def toggle_voice(self):
        if self.voice_input.is_listening:
            self.voice_input.stop()
        else:
            self.voice_input.start()

    def on_voice_status(self, status):
        if status == "listening":
            self.mic_btn.setText("LISTENING")
            self.mic_btn.setProperty("class", "recording")
            self.mic_btn.style().unpolish(self.mic_btn)
            self.mic_btn.style().polish(self.mic_btn)
            self.voice_label.setText("VOICE: LISTENING")
            self.voice_label.setStyleSheet("color: #ff6600; font-size: 11px; font-weight: bold;")
        elif status == "idle":
            self.mic_btn.setText("VOICE")
            self.mic_btn.setProperty("class", "")
            self.mic_btn.style().unpolish(self.mic_btn)
            self.mic_btn.style().polish(self.mic_btn)
            self.voice_label.setText("VOICE: READY")
            self.voice_label.setStyleSheet("color: rgba(0, 212, 255, 0.7); font-size: 11px;")
        elif status == "unavailable":
            self.mic_btn.setText("N/A")
            self.mic_btn.setEnabled(False)
            self.voice_label.setText("VOICE: UNAVAILABLE")
            self.voice_label.setStyleSheet("color: rgba(100, 100, 100, 0.7); font-size: 11px;")
        elif status == "error":
            self.mic_btn.setText("ERROR")
            self.voice_label.setText("VOICE: ERROR")

    def on_voice_heard(self, text):
        if text and text.strip():
            self.input_field.setText(text)
            self.send_message(text)

    def on_wake_triggered(self):
        msg = f"Hey Rutwik! I'm here. What do you need?"
        self.add_message(msg, False)
        self.voice.speak(msg)

        self.arc.pulse_wake()

    def on_wake_status(self, status):
        if status == "active":
            self.wake_label.setText("WAKE: Listening for claps...")
            self.wake_label.setStyleSheet("color: #00ff88; font-size: 10px; font-weight: bold;")
        elif status == "inactive":
            self.wake_label.setText("WAKE: Disabled")
            self.wake_label.setStyleSheet("color: rgba(100, 100, 100, 0.7); font-size: 10px;")

    def send_message(self, text=None):
        text = text or self.input_field.text().strip()
        if not text:
            return
        self.input_field.clear()
        self.add_message(text, True)
        self.conversation.append({"role": "user", "content": text})
        threading.Thread(target=self.get_response, args=(text,), daemon=True).start()

    def get_response(self, text):
        import urllib.request

        system_result = self.system.execute(text)
        if system_result is not None:
            self.add_message(f"[System] {system_result}", False)
            self.voice.speak(system_result)
            return

        try:
            start = time.time()
            data = json.dumps({"messages": self.conversation[-8:]}).encode()
            req = urllib.request.Request(
                f"{FRIDAY_SERVER}/chat",
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=30) as r:
                result = json.loads(r.read())
            elapsed = int((time.time() - start) * 1000)
            self.response_label.setText(f"RESPONSE: {elapsed}ms")
            reply = result.get("reply", "Processing complete, boss.")
        except Exception:
            reply = f"Connection disrupted, {YOUR_NAME}. All systems nominal. Try again."
        self.add_message(reply, False)
        self.voice.speak(reply)

    def closeEvent(self, event):
        self.wake_word.stop()
        self.voice_input.stop()
        super().closeEvent(event)


class SplashScreen(QSplashScreen):
    def __init__(self):
        from PyQt6.QtGui import QPixmap
        pixmap = QPixmap(500, 350)
        pixmap.fill(QColor(3, 8, 16))
        super().__init__(pixmap)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        label = QLabel("F.R.I.D.A.Y.", self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            color: #00d4ff;
            font-size: 52px;
            font-weight: bold;
            letter-spacing: 12px;
            background: transparent;
        """)
        label.setFont(QFont("Arial", 52, QFont.Weight.Bold))
        label.resize(500, 350)
        label.move(0, 120)
        sub = QLabel("FULLY RESPONSIVE INTELLIGENT DIGITAL ASSISTANT FOR YOU", self)
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet("color: rgba(0, 212, 255, 0.5); font-size: 10px; letter-spacing: 3px; background: transparent;")
        sub.setFont(QFont("Arial", 9))
        sub.resize(500, 350)
        sub.move(0, 195)
        self.show()
        QTimer.singleShot(3500, self.finish)

    def finish(self):
        self.window = FridayWindow()
        self.window.show()
        self.hide()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("F.R.I.D.A.Y.")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(3, 8, 16))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(200, 232, 240))
    app.setPalette(palette)
    splash = SplashScreen()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
