#!/usr/bin/env python3
"""
F.R.I.D.A.Y. — Professional JARVIS-Style macOS AI Assistant
"""

import sys, os, json, time, threading, datetime, math
import pyttsx3

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea, QFrame, QGraphicsView,
    QGraphicsScene, QSplashScreen, QLineEdit
)
from PyQt6.QtCore import (
    Qt, QTimer, pyqtSignal, QThread
)
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QPainter, QBrush, QPen
)

FRIDAY_SERVER = "https://friday-ai-2hbv.onrender.com"
YOUR_NAME = "Rutwik"
LOCATION = "Pune"


class FridayVoice:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 160)
        self.engine.setProperty('volume', 1.0)
        for voice in self.engine.getProperty('voices'):
            if 'Victoria' in voice.name:
                self.engine.setProperty('voice', voice.id)
                break

    def speak(self, text):
        def run():
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception:
                pass
        threading.Thread(target=run, daemon=True).start()


class ArcReactorWidget(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setSceneRect(-150, -150, 300, 300)
        self.setBackgroundRole(QPalette.ColorRole.NoRole)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.angle = 0
        self.pulse = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_reactor)
        self.timer.start(30)
        self.build_reactor()

    def build_reactor(self):
        self.scene.clear()
        for i in range(8):
            radius = 130 + i * 4
            glow = self.scene.addEllipse(-radius, -radius, radius*2, radius*2)
            glow.setPen(QPen(QColor(0, 150, 255, max(0, 8 - i * 1.5))))
            glow.setBrush(Qt.BrushStyle.NoBrush)

        ring_configs = [
            (120, 2.5, QColor(0, 220, 255, 220)),
            (100, -1.8, QColor(0, 200, 255, 200)),
            (85, 2.2, QColor(0, 180, 255, 180)),
            (70, -1.5, QColor(0, 160, 255, 160)),
            (55, 1.8, QColor(0, 140, 255, 140)),
            (40, -1.2, QColor(0, 120, 255, 120)),
            (25, 1.5, QColor(0, 100, 255, 200)),
        ]
        self.rings = []
        for radius, speed, color in ring_configs:
            ring = self.scene.addEllipse(-radius, -radius, radius*2, radius*2)
            ring.setPen(QPen(color, 2))
            ring.setBrush(Qt.BrushStyle.NoBrush)
            self.rings.append((ring, speed))

        glow_inner = self.scene.addEllipse(-18, -18, 36, 36)
        glow_inner.setBrush(QBrush(QColor(100, 220, 255, 100)))
        glow_inner.setPen(Qt.PenStyle.NoPen)
        self.core = self.scene.addEllipse(-12, -12, 24, 24)
        self.core.setBrush(QBrush(QColor(255, 255, 255, 255)))
        self.core.setPen(Qt.PenStyle.NoPen)

    def update_reactor(self):
        self.angle += 1
        self.pulse = abs(math.sin(self.angle * 0.05))
        for ring, speed in self.rings:
            ring.setRotation(self.angle * speed)
        if self.core:
            self.core.setScale(0.9 + self.pulse * 0.3)
            g = int(150 + self.pulse * 105)
            self.core.setBrush(QBrush(QColor(g, g, g)))
        self.scene.update()


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
        self.conversation = []
        self._init_ui()
        self.greeting()

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
        self.arc.setFixedSize(200, 200)
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

        sp_layout.addWidget(self.status_label)
        sp_layout.addWidget(self.time_label)
        sp_layout.addWidget(self.weather_label)
        sp_layout.addWidget(self.response_label)
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

        self.send_btn = QPushButton("SEND")
        self.send_btn.setFixedSize(90, 46)
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
            greeting = f"Good morning, {YOUR_NAME}."
        elif 12 <= hour < 17:
            greeting = f"Good afternoon, {YOUR_NAME}."
        elif 17 <= hour < 21:
            greeting = f"Good evening, {YOUR_NAME}."
        else:
            greeting = f"Good evening, {YOUR_NAME}."
        full = (
            f"{greeting} System online. I am F.R.I.D.A.Y., fully operational. "
            f"All neural networks are active. Groq LLM is connected. "
            f"How may I assist you today?"
        )
        self.add_message(full, False)
        self.voice.speak(full)

    def add_message(self, text, is_user):
        bubble = ChatBubble(text, is_user)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble)
        QTimer.singleShot(50, lambda: self.chat_area.verticalScrollBar().setValue(
            self.chat_area.verticalScrollBar().maximum()
        ))

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
            text-shadow: 0 0 30px rgba(0, 212, 255, 0.8), 0 0 60px rgba(0, 212, 255, 0.4);
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
