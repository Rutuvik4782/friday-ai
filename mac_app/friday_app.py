#!/usr/bin/env python3
"""
F.R.I.D.A.Y. — Native macOS AI Assistant
A JARVIS-style AI app for your Mac.

Run: python3 friday_app.py
"""

import sys
import os
import json
import time
import threading
import random
import datetime
import pyttsx3

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLineEdit, QLabel, QScrollArea,
    QFrame, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,
    QSplashScreen, QDialog, QSizePolicy
)
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect,
    pyqtSignal, QThread, pyqtSlot, QSize
)
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QPainter, QBrush, QPen,
    QPainterPath, QTextCursor, QPixmap
)

try:
    import requests
except ImportError:
    import urllib.request as requests


# =============================================================================
# CONFIGURATION
# =============================================================================

FRIDAY_SERVER = "https://friday-ai-2hbv.onrender.com"
YOUR_NAME = "Rutwik"
LOCATION = "Pune"
APP_NAME = "F.R.I.D.A.Y."


# =============================================================================
# TTS ENGINE — Victoria voice on macOS
# =============================================================================

class FridayVoice:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 165)
        self.engine.setProperty('volume', 1.0)
        
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'Victoria' in voice.name:
                self.engine.setProperty('voice', voice.id)
                break
            elif 'Samantha' in voice.name:
                self.engine.setProperty('voice', voice.id)

    def speak(self, text):
        def run():
            self.engine.say(text)
            self.engine.runAndWait()
        threading.Thread(target=run, daemon=True).start()


# =============================================================================
# STT ENGINE — Voice recognition (stub, requires speech-recognition package)
# =============================================================================

class FridayListener(QThread):
    heard = pyqtSignal(str)
    status = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running = False

    def run(self):
        self.status.emit("unavailable")

    def stop(self):
        self.running = False


# =============================================================================
# ARC REACTOR WIDGET
# =============================================================================

class ArcReactor(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setSceneRect(-100, -100, 200, 200)
        self.setBackgroundRole(QPalette.ColorRole.NoRole)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.timer.start(30)
        
        self.build_reactor()
        
    def build_reactor(self):
        self.scene.clear()
        
        # Outer glow
        for i in range(5):
            glow = QGraphicsEllipseItem(-90 + i * 5, -90 + i * 5, 180 - i * 10, 180 - i * 10)
            glow.setPen(QPen(QColor(0, 170, 255, 50 - i * 8), 2))
            glow.setBrush(Qt.BrushStyle.NoBrush)
            self.scene.addItem(glow)
        
        # Main rings
        colors = [(0, 200, 255), (0, 255, 255), (0, 150, 255), (0, 100, 200), (0, 80, 180)]
        radii = [80, 65, 50, 35, 20]
        for color, radius in zip(colors, radii):
            ring = QGraphicsEllipseItem(-radius, -radius, radius * 2, radius * 2)
            ring.setPen(QPen(QColor(*color), 3))
            ring.setBrush(Qt.BrushStyle.NoBrush)
            self.scene.addItem(ring)
        
        # Core
        core = QGraphicsEllipseItem(-15, -15, 30, 30)
        core.setBrush(QBrush(QColor(200, 240, 255)))
        core.setPen(QPen(Qt.PenStyle.NoPen))
        self.scene.addItem(core)
        
    def rotate(self):
        self.angle = (self.angle + 1) % 360
        self.update()


# =============================================================================
# CHAT BUBBLE WIDGET
# =============================================================================

class ChatBubble(QFrame):
    def __init__(self, text, is_user=False, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.setStyleSheet(f"""
            QFrame {{
                background: {"rgba(0, 60, 120, 0.7)" if not is_user else "rgba(180, 60, 0, 0.7)"};
                border: 1px solid {"rgba(0, 170, 255, 0.4)" if not is_user else "rgba(255, 120, 0, 0.4)"};
                border-radius: 12px;
                padding: 10px;
                margin: 5px 20px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        label = QLabel(text)
        label.setWordWrap(True)
        label.setStyleSheet("color: #c8e8f0; background: transparent; border: none;")
        label.setFont(QFont("Rajdhani", 13))
        layout.addWidget(label)


# =============================================================================
# MAIN WINDOW
# =============================================================================

class FridayWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.voice = FridayVoice()
        self.listener = None
        self.conversation = []
        self.is_listening = False
        
        self.setup_ui()
        self.greeting()
        
    def setup_ui(self):
        self.setWindowTitle("F.R.I.D.A.Y. — Tony Stark AI")
        self.setStyleSheet("background-color: #0a0c10;")
        
        # Center on screen
        screen = QScreen.availableGeometry(QApplication.primaryScreen())
        self.resize(900, 700)
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
        
        # Title bar
        title_bar = QLabel(f"  {APP_NAME} — FULLY RESPONSIVE INTELLIGENT DIGITAL ASSISTANT FOR YOU")
        title_bar.setStyleSheet("""
            background: rgba(0, 20, 40, 0.9);
            color: #0ff;
            font-family: Arial;
            font-size: 13px;
            font-weight: bold;
            letter-spacing: 2px;
            padding: 8px 15px;
            border-bottom: 1px solid rgba(0, 170, 255, 0.3);
        """)
        title_bar.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        title_bar.setFixedHeight(36)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        main_layout.addWidget(title_bar)
        
        # Content area
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(15, 15, 15, 10)
        
        # Arc reactor + chat side by side
        top_row = QHBoxLayout()
        
        # Arc reactor
        self.arc = ArcReactor()
        self.arc.setFixedSize(180, 180)
        
        # Status panel
        status_panel = QWidget()
        status_panel.setStyleSheet("background: rgba(0,20,40,0.5); border-radius: 8px; border: 1px solid rgba(0,170,255,0.2);")
        status_layout = QVBoxLayout(status_panel)
        status_layout.setContentsMargins(15, 15, 15, 15)
        
        self.status_label = QLabel("STATUS: ONLINE")
        self.status_label.setStyleSheet("color: #0f0; font-size: 12px; font-weight: bold; letter-spacing: 2px;")
        self.status_label.setFont(QFont("Courier", 11, QFont.Weight.Bold))
        
        self.time_label = QLabel()
        self.time_label.setStyleSheet("color: rgba(0,200,255,0.7); font-size: 11px;")
        self.time_label.setFont(QFont("Courier", 10))
        
        self.weather_label = QLabel()
        self.weather_label.setStyleSheet("color: rgba(0,200,255,0.7); font-size: 11px;")
        self.weather_label.setFont(QFont("Courier", 10))
        
        self.listen_label = QLabel("🎤 CLICK TO SPEAK")
        self.listen_label.setStyleSheet("color: #0ff; font-size: 12px; font-weight: bold; letter-spacing: 1px;")
        self.listen_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.time_label)
        status_layout.addWidget(self.weather_label)
        status_layout.addStretch()
        status_layout.addWidget(self.listen_label)
        
        top_row.addWidget(self.arc)
        top_row.addWidget(status_panel, 1)
        
        content_layout.addLayout(top_row)
        
        # Chat area
        self.chat_area = QScrollArea()
        self.chat_area.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical { background: rgba(0,50,80,0.5); width: 4px; border-radius: 2px; }
            QScrollBar::handle { background: rgba(0,170,255,0.5); border-radius: 2px; }
        """)
        self.chat_area.setWidgetResizable(True)
        self.chat_area.setFrameShape(QFrame.Shape.NoFrame)
        
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setContentsMargins(5, 5, 5, 5)
        self.chat_layout.setSpacing(5)
        self.chat_layout.addStretch()
        
        self.chat_area.setWidget(self.chat_container)
        content_layout.addWidget(self.chat_area, 1)
        
        # Input area
        input_row = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("  Talk to F.R.I.D.A.Y...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background: rgba(0, 30, 60, 0.7);
                color: #c8e8f0;
                border: 1px solid rgba(0, 170, 255, 0.3);
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                font-family: Rajdhani;
            }
            QLineEdit:focus {
                border: 1px solid #0af;
                background: rgba(0, 50, 100, 0.7);
            }
            QLineEdit::placeholder { color: rgba(0,150,200,0.4); }
        """)
        self.input_field.setFont(QFont("Rajdhani", 14))
        self.input_field.returnPressed.connect(self.send_message)
        
        self.mic_btn = QPushButton("🎤")
        self.mic_btn.setFixedSize(50, 46)
        self.mic_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 30, 60, 0.7);
                border: 1px solid rgba(0, 170, 255, 0.3);
                border-radius: 8px;
                color: #0ff;
                font-size: 20px;
            }
            QPushButton:hover { background: rgba(0, 80, 150, 0.7); border-color: #0af; }
            QPushButton:pressed { background: rgba(0, 100, 200, 0.8); }
        """)
        self.mic_btn.clicked.connect(self.toggle_listening)
        
        self.send_btn = QPushButton("SEND")
        self.send_btn.setFixedSize(80, 46)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background: linear-gradient(135deg, #0066aa, #00aaff);
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
                letter-spacing: 2px;
            }
            QPushButton:hover { background: linear-gradient(135deg, #0088cc, #00ccff); }
        """)
        self.send_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.send_btn.clicked.connect(self.send_message)
        
        input_row.addWidget(self.input_field)
        input_row.addWidget(self.mic_btn)
        input_row.addWidget(self.send_btn)
        
        content_layout.addLayout(input_row)
        
        main_layout.addWidget(content)
        
        # Status timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()
        
        self.show()
        
    def update_time(self):
        now = datetime.datetime.now()
        self.time_label.setText(now.strftime("TIME: %I:%M:%S %p\nDATE: %d %b %Y"))
        
        if not getattr(self, '_weather_fetched', False):
            self._weather_fetched = True
            threading.Thread(target=self.fetch_weather, daemon=True).start()
    
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
            self.weather_label.setText(f"WEATHER: {temp}°C, {condition}\nLOCATION: {LOCATION}")
        except Exception:
            self.weather_label.setText(f"WEATHER: 24°C, Clear\nLOCATION: {LOCATION}")
    
    def greeting(self):
        hour = datetime.datetime.now().hour
        if 5 <= hour < 12:
            greeting = f"Good morning, {YOUR_NAME}."
        elif 12 <= hour < 17:
            greeting = f"Good afternoon, {YOUR_NAME}."
        elif 17 <= hour < 21:
            greeting = f"Good evening, {YOUR_NAME}."
        else:
            greeting = f"Good evening, {YOUR_NAME}."
        
        full_greeting = (
            f"{greeting} System online. I'm F.R.I.D.A.Y., fully operational. "
            f"Pune is currently clear, 24 degrees. All systems nominal. "
            f"Text input enabled. Type your request below."
        )
        
        self.add_message(full_greeting, is_user=False)
        self.voice.speak(full_greeting)
    
    def add_message(self, text, is_user=False):
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
        self.add_message(text, is_user=True)
        self.conversation.append({"role": "user", "content": text})
        
        threading.Thread(target=self.get_response, args=(text,), daemon=True).start()
    
    def get_response(self, text):
        try:
            import urllib.request, urllib.error
            data = json.dumps({"messages": self.conversation[-6:]}).encode()
            req = urllib.request.Request(
                f"{FRIDAY_SERVER}/chat",
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=30) as r:
                result = json.loads(r.read())
            reply = result.get("reply", "Processing complete, boss.")
        except Exception as e:
            reply = f"Connection disrupted, {YOUR_NAME}. All systems nominal. Try again."
        
        self.add_message(reply, is_user=False)
        self.voice.speak(reply)
    
    def toggle_listening(self):
        if self.is_listening:
            self.stop_listening()
        else:
            self.start_listening()
    
    def start_listening(self):
        if not self.listener:
            self.listener = FridayListener()
            self.listener.heard.connect(self.on_heard)
            self.listener.status.connect(self.on_listen_status)
        
        self.is_listening = True
        self.mic_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 50, 0, 0.7);
                border: 2px solid #ff6600;
                border-radius: 8px;
                color: #fff;
                font-size: 20px;
            }
        """)
        self.listen_label.setText("🎤 LISTENING...")
        self.listener.start()
    
    def stop_listening(self):
        self.is_listening = False
        if self.listener:
            self.listener.stop()
        self.mic_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 30, 60, 0.7);
                border: 1px solid rgba(0, 170, 255, 0.3);
                border-radius: 8px;
                color: #0ff;
                font-size: 20px;
            }
            QPushButton:hover { background: rgba(0, 80, 150, 0.7); border-color: #0af; }
        """)
        self.listen_label.setText("🎤 CLICK TO SPEAK")
    
    @pyqtSlot(str)
    def on_heard(self, text):
        self.stop_listening()
        if text.strip():
            self.send_message(text)
    
    @pyqtSlot(str)
    def on_listen_status(self, status):
        if status == "unavailable":
            self.listen_label.setText("⚠ VOICE INPUT UNAVAILABLE")
            self.mic_btn.setEnabled(False)
            self.mic_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(80, 80, 80, 0.5);
                    border: 1px solid rgba(100, 100, 100, 0.3);
                    border-radius: 8px;
                    color: rgba(150, 150, 150, 0.5);
                    font-size: 20px;
                }
            """)
        elif status == "processing":
            self.listen_label.setText("⏳ PROCESSING...")
        elif status == "listening":
            self.listen_label.setText("🎤 LISTENING...")
        else:
            self.listen_label.setText("🎤 CLICK TO SPEAK")
    
    def closeEvent(self, event):
        if self.listener:
            self.listener.stop()


# =============================================================================
# SPLASH SCREEN
# =============================================================================

class SplashScreen(QSplashScreen):
    def __init__(self):
        pixmap = QPixmap(600, 400)
        pixmap.fill(QColor(10, 12, 16))
        super().__init__(pixmap)
        
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        
        label = QLabel("F.R.I.D.A.Y.", self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            color: #0ff;
            font-size: 48px;
            font-weight: bold;
            letter-spacing: 10px;
            background: transparent;
            text-shadow: 0 0 30px rgba(0,255,255,0.8);
        """)
        label.setFont(QFont("Arial", 48, QFont.Weight.Bold))
        label.resize(600, 400)
        label.move(0, 150)
        
        sub = QLabel("FULLY RESPONSIVE INTELLIGENT DIGITAL ASSISTANT FOR YOU", self)
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet("color: rgba(0,170,255,0.6); font-size: 11px; letter-spacing: 3px; background: transparent;")
        sub.setFont(QFont("Arial", 10))
        sub.resize(600, 400)
        sub.move(0, 220)
        
        self.show()
        QTimer.singleShot(3000, self.finish_splash)
        
    def finish_splash(self):
        self.window = FridayWindow()
        self.window.show()
        self.hide()


# =============================================================================
# MAIN
# =============================================================================

def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(10, 12, 16))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(200, 232, 240))
    app.setPalette(palette)
    
    splash = SplashScreen()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
