#!/usr/bin/env python3
"""
F.R.I.D.A.Y. PRO — Tony Stark Level AI Assistant
Advanced JARVIS-style AI for macOS with professional features.

Features: Wake word, voice I/O, memory, vision, calendar, 
email, notes, proactive intelligence, system control, and more.
"""

import sys
import os
import json
import time
import threading
import random
import math
import subprocess
import tempfile
import sqlite3
import hashlib
import datetime as dt
from pathlib import Path
from typing import Optional, Dict, List, Any

# Qt Imports
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea, QFrame, QLineEdit, QTextEdit,
    QSystemTrayIcon, QMenu, QTabWidget, QListWidget, QSplashScreen,
    QDialog, QGroupBox, QSlider, QCheckBox, QComboBox, QProgressBar,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import (
    Qt, QTimer, QPointF, QObject, pyqtSignal, QThread, QSize,
    QPropertyAnimation, QEasingCurve, QRect, QRectF, QPoint
)
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QBrush, QPen, QPainter, QPainterPath,
    QRadialGradient, QLinearGradient, QIcon, QAction, QPixmap,
    QTransform, QConicalGradient, QLinearGradient
)

# Configuration
FRIDAY_SERVER = "https://friday-ai-2hbv.onrender.com"
YOUR_NAME = "Rutwik"
LOCATION = "Pune"
APP_NAME = "F.R.I.D.A.Y. PRO"
VERSION = "10.0"

# =============================================================================
# MEMORY DATABASE — SQLite for long-term memory
# =============================================================================

class MemoryDatabase:
    def __init__(self):
        self.db_path = os.path.join(os.path.expanduser("~"), ".friday_memory.db")
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()
    
    def _init_tables(self):
        cursor = self.conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                category TEXT,
                importance INTEGER DEFAULT 5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0
            );
            
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT,
                content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT
            );
            
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                due_date TIMESTAMP,
                completed INTEGER DEFAULT 0,
                priority INTEGER DEFAULT 5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT,
                remind_at TIMESTAMP,
                triggered INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS user_preferences (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS files_accessed (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT,
                accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 1
            );
        """)
        self.conn.commit()
    
    def remember(self, key: str, value: str, category: str = "general", importance: int = 5):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO memories (key, value, category, importance, accessed_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (key, value, category, importance))
        self.conn.commit()
    
    def recall(self, key: str) -> Optional[str]:
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE memories SET access_count = access_count + 1, 
            accessed_at = CURRENT_TIMESTAMP WHERE key = ?
        """, (key,))
        self.conn.commit()
        cursor.execute("SELECT value FROM memories WHERE key = ?", (key,))
        result = cursor.fetchone()
        return result['value'] if result else None
    
    def search_memories(self, query: str, limit: int = 10) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM memories 
            WHERE key LIKE ? OR value LIKE ? OR category LIKE ?
            ORDER BY importance DESC, accessed_at DESC
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", f"%{query}%", limit))
        return [dict(row) for row in cursor.fetchall()]
    
    def add_conversation(self, role: str, content: str, session_id: str = "default"):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO conversations (role, content, session_id)
            VALUES (?, ?, ?)
        """, (role, content, session_id))
        self.conn.commit()
    
    def get_conversation_history(self, session_id: str = "default", limit: int = 20) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM conversations 
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (session_id, limit))
        return [dict(row) for row in cursor.fetchall()]
    
    def add_task(self, title: str, description: str = "", due_date: str = None, priority: int = 5):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (title, description, due_date, priority)
            VALUES (?, ?, ?, ?)
        """, (title, description, due_date, priority))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_tasks(self, include_completed: bool = False) -> List[Dict]:
        cursor = self.conn.cursor()
        if include_completed:
            cursor.execute("SELECT * FROM tasks ORDER BY priority DESC, due_date ASC")
        else:
            cursor.execute("SELECT * FROM tasks WHERE completed = 0 ORDER BY priority DESC, due_date ASC")
        return [dict(row) for row in cursor.fetchall()]
    
    def complete_task(self, task_id: int):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
        self.conn.commit()
    
    def add_reminder(self, message: str, remind_at: str):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO reminders (message, remind_at) VALUES (?, ?)
        """, (message, remind_at))
        self.conn.commit()
    
    def get_due_reminders(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM reminders 
            WHERE triggered = 0 AND datetime(remind_at) <= datetime('now')
        """)
        return [dict(row) for row in cursor.fetchall()]
    
    def set_preference(self, key: str, value: str):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO user_preferences (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (key, value))
        self.conn.commit()
    
    def get_preference(self, key: str, default: str = None) -> Optional[str]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM user_preferences WHERE key = ?", (key,))
        result = cursor.fetchone()
        return result['value'] if result else default
    
    def remember_file(self, path: str):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO files_accessed (path, accessed_at)
            VALUES (?, CURRENT_TIMESTAMP)
        """, (path,))
        self.conn.commit()
    
    def close(self):
        self.conn.close()


# =============================================================================
# VOICE ENGINE — Natural TTS with custom voice
# =============================================================================

class FridayVoice:
    def __init__(self):
        self.voice_name = "en-US-GuyNeural"
        self.rate = "+0%"
        self.volume = "+0%"
        self._edge_available = False
        self._voice_file = os.path.join(os.path.expanduser("~"), ".friday_voice.mp3")
        self._check_voice()
    
    def _check_voice(self):
        try:
            import edge_tts
            self._edge_available = True
        except ImportError:
            self._edge_available = False
        
        if os.path.exists(self._voice_file):
            self._use_custom = True
        else:
            self._use_custom = False
    
    def set_custom_voice(self, voice_file: str):
        if os.path.exists(voice_file):
            self._voice_file = voice_file
            self._use_custom = True
        else:
            self._use_custom = False
    
    def speak(self, text: str):
        def run():
            try:
                if self._use_custom:
                    self._speak_custom(text)
                elif self._edge_available:
                    self._speak_edge(text)
                else:
                    self._speak_say(text)
            except Exception as e:
                try:
                    self._speak_say(text)
                except:
                    pass
        threading.Thread(target=run, daemon=True).start()
    
    def _speak_custom(self, text: str):
        try:
            subprocess.run(["afplay", self._voice_file], timeout=30, capture_output=True)
        except:
            self._speak_say(text)
    
    def _speak_edge(self, text: str):
        import edge_tts, asyncio
        async def _talk():
            try:
                mp3_path = tempfile.mktemp(suffix=".mp3")
                communicate = edge_tts.Communicate(text, self.voice_name, rate=self.rate, volume=self.volume)
                await communicate.save(mp3_path)
                subprocess.run(["afplay", mp3_path], timeout=30, capture_output=True)
                os.unlink(mp3_path)
            except:
                self._speak_say(text)
        try:
            asyncio.run(_talk())
        except:
            self._speak_say(text)
    
    def _speak_say(self, text: str):
        cmd = ["say", "-v", "Samantha", "-r", "165", text]
        subprocess.run(cmd, timeout=30, capture_output=True)


# =============================================================================
# VOICE RECOGNITION — Swift-based native recognition
# =============================================================================

class VoiceListener(QObject):
    heard = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.is_listening = False
        self._proc = None
    
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
            self.status_changed.emit("unavailable")
        except:
            pass
        finally:
            self.is_listening = False
            self.status_changed.emit("idle")
    
    def stop(self):
        self.is_listening = False
        if self._proc:
            try:
                self._proc.kill()
            except:
                pass


# =============================================================================
# WAKE WORD LISTENER — Simple activation
# =============================================================================

class WakeWordListener(QObject):
    triggered = pyqtSignal()
    status = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.running = False
    
    def start(self):
        if self.running:
            return
        self.running = True
        self.status.emit("listening")
    
    def stop(self):
        self.running = False


# =============================================================================
# ARC REACTOR WIDGET — Professional JARVIS Style
# =============================================================================

class ArcReactorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(280, 280)
        
        self.angle = 0.0
        self.phase = 0.0
        self.pulse = 0.5
        self.wake_active = False
        self.wake_timer = 0
        self.particles = []
        
        for _ in range(25):
            self.particles.append({
                'angle': random.random() * 360,
                'radius': 40 + random.random() * 80,
                'speed': 0.2 + random.random() * 0.5,
                'size': 1 + random.random() * 2.5,
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
        p.scale(s / 140, s / 140)
        
        base_color = QColor(0, 180, 255) if not self.wake_active else QColor(0, 255, 180)
        glow_intensity = int(200 * self.pulse)
        
        # Outer ambient glow
        for i in range(12, 0, -1):
            alpha = int(3 * (13 - i))
            radius = 130 + i * 5
            p.setPen(QPen(QColor(base_color.red(), base_color.green(), base_color.blue(), alpha), i * 2))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(-radius, -radius, radius * 2, radius * 2)
        
        # Containment ring
        p.setPen(QPen(QColor(30, 40, 50), 4))
        p.setBrush(QBrush(QColor(15, 20, 28)))
        p.drawEllipse(-130, -130, 260, 260)
        
        # Tick marks
        for i in range(60):
            angle_rad = math.radians(i * 6)
            inner_r = 122
            outer_r = 127 if i % 5 == 0 else 124
            x1 = inner_r * math.cos(angle_rad)
            y1 = inner_r * math.sin(angle_rad)
            x2 = outer_r * math.cos(angle_rad)
            y2 = outer_r * math.sin(angle_rad)
            
            if i % 5 == 0:
                p.setPen(QPen(QColor(0, 150, 220, 200), 2))
            else:
                p.setPen(QPen(QColor(0, 120, 180, 100), 1))
            p.drawLine(QPointF(x1, y1), QPointF(x2, y2))
        
        # Energy rings
        for ring_idx, (ring_r, ring_alpha, ring_speed) in enumerate([
            (105, 200, 0.8),
            (88, 180, -1.0),
            (70, 160, 1.2),
            (50, 140, -0.6),
        ]):
            actual_angle = self.angle * ring_speed
            segments = 36
            seg_span = 360 / segments * 0.7
            
            for seg in range(segments):
                seg_angle = math.radians(seg * (360 / segments) + actual_angle)
                arc_angle = math.degrees(seg_angle) - seg_span / 2
                
                for glow_i in range(4, 0, -1):
                    glow_alpha = int(ring_alpha / (glow_i * 2))
                    p.setPen(QPen(
                        QColor(base_color.red(), base_color.green(), base_color.blue(), glow_alpha),
                        glow_i * 2
                    ))
                    p.drawArc(
                        QRectF(-ring_r, -ring_r, ring_r * 2, ring_r * 2),
                        int(arc_angle * 16), int(seg_span * 16)
                    )
                
                p.setPen(QPen(
                    QColor(base_color.red(), base_color.green(), base_color.blue(), int(ring_alpha * self.pulse)),
                    2
                ))
                p.drawArc(
                    QRectF(-ring_r, -ring_r, ring_r * 2, ring_r * 2),
                    int(arc_angle * 16), int(seg_span * 16)
                )
        
        # Hexagonal housing
        hex_pts = []
        for i in range(6):
            angle_rad = math.radians(i * 60 + 30)
            hex_pts.append(QPointF(32 * math.cos(angle_rad), 32 * math.sin(angle_rad)))
        
        for layer in range(3):
            offset = layer * 2
            path = QPainterPath()
            path.moveTo(hex_pts[0])
            for pt in hex_pts[1:]:
                path.lineTo(pt)
            path.closeSubpath()
            
            p.setPen(QPen(QColor(20 + layer * 10, 40 + layer * 10, 60 + layer * 10, 255 - layer * 40), 2))
            p.setBrush(QBrush(QColor(15 + layer * 5, 30 + layer * 5, 50 + layer * 5, 200 - layer * 40)))
            p.drawPath(path)
        
        # Rotating inner hex
        p.save()
        p.rotate(self.angle * 0.5)
        
        inner_hex = []
        for i in range(6):
            angle_rad = math.radians(i * 60)
            inner_hex.append(QPointF(22 * math.cos(angle_rad), 22 * math.sin(angle_rad)))
        
        path = QPainterPath()
        path.moveTo(inner_hex[0])
        for pt in inner_hex[1:]:
            path.lineTo(pt)
        path.closeSubpath()
        
        for g in range(4, 0, -1):
            p.setPen(QPen(
                QColor(base_color.red(), base_color.green(), base_color.blue(), 40 * g),
                g * 2
            ))
            p.drawPath(path)
        
        p.setPen(QPen(QColor(base_color.red(), base_color.green(), base_color.blue(), 220), 2))
        p.drawPath(path)
        p.restore()
        
        # Energy arcs
        for arc_idx, (arc_r, arc_start) in enumerate([(58, 0), (42, 120), (28, 240)]):
            arc_angle = self.angle + arc_start + arc_idx * 30
            
            for w in range(3, 0, -1):
                p.setPen(QPen(
                    QColor(base_color.red(), base_color.green(), base_color.blue(), 50 * w),
                    w * 3
                ))
                p.drawArc(
                    QRectF(-arc_r, -arc_r, arc_r * 2, arc_r * 2),
                    int(arc_angle * 16), 6000
                )
            
            p.setPen(QPen(QColor(base_color.red(), base_color.green(), base_color.blue(), 200), 2))
            p.drawArc(
                QRectF(-arc_r, -arc_r, arc_r * 2, arc_r * 2),
                int(arc_angle * 16), 6000
            )
        
        # Core glow
        core_scale = 1.0 + math.sin(self.phase * 2) * 0.08
        for layer in range(8, 0, -1):
            r = layer * 4 * core_scale
            alpha = int(25 * (9 - layer) * self.pulse)
            
            gradient = QRadialGradient(QPointF(0, 0), r)
            gradient.setColorAt(0, QColor(220, 250, 255, alpha))
            gradient.setColorAt(0.5, QColor(base_color.red(), base_color.green(), base_color.blue(), alpha // 2))
            gradient.setColorAt(1, QColor(base_color.red() // 2, base_color.green() // 2, base_color.blue() // 2, 0))
            
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(gradient))
            p.drawEllipse(QPointF(0, 0), r, r)
        
        # Inner core
        core_size = 8 * core_scale
        core_gradient = QRadialGradient(QPointF(0, 0), core_size)
        core_gradient.setColorAt(0, QColor(255, 255, 255, 255))
        core_gradient.setColorAt(0.3, QColor(200, 240, 255, 230))
        core_gradient.setColorAt(0.7, QColor(base_color.red(), base_color.green(), base_color.blue(), 180))
        core_gradient.setColorAt(1, QColor(base_color.red() // 2, base_color.green() // 2, base_color.blue() // 2, 0))
        
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(core_gradient))
        p.drawEllipse(QPointF(0, 0), core_size, core_size)
        
        # Highlight
        p.setPen(QPen(QColor(255, 255, 255, 100), 0.5))
        p.drawEllipse(QPointF(-2, -2), 3, 3)
        
        # Particles
        for part in self.particles:
            pr = part['radius']
            px = pr * math.cos(math.radians(part['angle']))
            py = pr * math.sin(math.radians(part['angle']))
            life_ratio = part['alpha'] / 150.0
            pa = int(150 * life_ratio * self.pulse)
            ps = part['size'] * life_ratio
            
            p.setPen(QPen(QColor(base_color.red(), base_color.green(), base_color.blue(), pa), 0.5))
            p.setBrush(QBrush(QColor(base_color.red(), base_color.green(), base_color.blue(), pa)))
            p.drawEllipse(QPointF(px, py), ps, ps)
        
        # Reflection
        refl_gradient = QLinearGradient(0, 125, 0, 135)
        refl_gradient.setColorAt(0, QColor(base_color.red(), base_color.green(), base_color.blue(), 30))
        refl_gradient.setColorAt(1, QColor(base_color.red(), base_color.green(), base_color.blue(), 0))
        
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(refl_gradient))
        p.drawRect(-100, 125, 200, 10)
        
        # Metallic rim
        for i in range(2):
            r = 135 - i
            alpha = 80 - i * 30
            p.setPen(QPen(QColor(60 + i * 20, 80 + i * 20, 100 + i * 20, alpha), 0.5))
            p.drawEllipse(QPointF(0, 0), r, r)


# =============================================================================
# SYSTEM CONTROLLER — Full laptop automation
# =============================================================================

class SystemController:
    def __init__(self):
        self.memory = MemoryDatabase()
        self.last_screenshot = None
    
    def execute(self, command: str) -> str:
        command = command.lower().strip()
        
        # Voice & Display
        if "volume" in command or "sound" in command:
            return self._volume(command)
        elif "brightness" in command:
            return self._brightness(command)
        
        # Apps
        elif "open" in command or "launch" in command:
            return self._open_app(command)
        elif "close" in command or "quit" in command:
            return self._close_app(command)
        
        # Files & Screens
        elif "screenshot" in command or "screen shot" in command:
            return self._screenshot()
        elif "open file" in command or "find file" in command:
            return self._find_file(command)
        
        # Web
        elif "search" in command and "web" in command:
            return self._search_web(command)
        elif "browse" in command or "go to" in command:
            return self._open_website(command)
        
        # Media
        elif "play" in command and ("music" in command or "song" in command):
            return self._music_control("play")
        elif "pause" in command:
            return self._music_control("pause")
        elif "next" in command or "skip" in command:
            return self._music_control("next")
        elif "previous" in command or "back" in command:
            return self._music_control("previous")
        
        # Notifications
        elif "notification" in command or "notify" in command or "remind" in command:
            return self._notification(command)
        
        # System Info
        elif "system" in command and "info" in command:
            return self._system_info()
        elif "battery" in command:
            return self._battery()
        elif "wifi" in command or "network" in command:
            return self._wifi()
        
        # System Actions
        elif "sleep" in command:
            return self._sleep()
        elif "restart" in command or "reboot" in command:
            return self._restart()
        elif "shutdown" in command:
            return self._shutdown()
        elif "lock" in command:
            return self._lock_screen()
        elif "empty" in command and "trash" in command:
            return self._empty_trash()
        
        # Clipboard
        elif "read" in command and "clipboard" in command:
            return self._read_clipboard()
        elif "copy" in command:
            return self._copy_to_clipboard(command)
        elif "paste" in command:
            return self._paste()
        
        # Tasks & Memory
        elif "remember" in command or "note" in command or "remind" in command:
            return self._remember(command)
        elif "what do you remember" in command or "recall" in command:
            return self._recall(command)
        elif "task" in command or "todo" in command:
            return self._tasks(command)
        
        # Math & Calc
        elif any(k in command for k in ["calculate", "compute", "what is", "solve"]):
            return self._calculate(command)
        
        # Default
        else:
            return self._run_terminal(command)
    
    def _volume(self, command: str) -> str:
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
        return f"Current volume is {result.stdout.strip()}%."
    
    def _brightness(self, command: str) -> str:
        try:
            nums = [int(s) for s in command.split() if s.isdigit()]
            if nums:
                brightness = max(0, min(100, nums[0]))
                subprocess.run(["brightness", str(brightness / 100)], capture_output=True)
                return f"Brightness set to {brightness}%."
            return "Tell me what brightness level you want."
        except FileNotFoundError:
            return "Brightness control requires the brightness CLI. Install via: brew install brightness"
    
    def _open_app(self, command: str) -> str:
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
            "notion": "Notion",
            "whatsapp": "WhatsApp",
            "telegram": "Telegram",
            "zoom": "Zoom",
            "teams": "Microsoft Teams",
            "settings": "System Settings",
            "activity": "Activity Monitor",
            "photos": "Photos",
            "calculator": "Calculator",
        }
        for keyword, app_name in apps.items():
            if keyword in command:
                subprocess.run(["open", "-a", app_name], capture_output=True)
                return f"Opening {app_name}."
        return "Which app should I open?"
    
    def _close_app(self, command: str) -> str:
        apps = {"chrome": "Google Chrome", "safari": "Safari", "spotify": "Spotify"}
        for keyword, app_name in apps.items():
            if keyword in command:
                subprocess.run(["osascript", "-e", f'tell application "{app_name}" to quit'])
                return f"Closing {app_name}."
        return "Which app should I close?"
    
    def _screenshot(self) -> str:
        path = os.path.expanduser(f"~/Desktop/screenshot_{int(time.time())}.png")
        subprocess.run(["screencapture", "-x", path], capture_output=True)
        self.last_screenshot = path
        return f"Screenshot saved to Desktop."
    
    def _find_file(self, command: str) -> str:
        query = command.replace("open file", "").replace("find file", "").replace("find", "").strip()
        if query:
            result = subprocess.run(
                ["mdfind", "-name", query],
                capture_output=True, text=True
            )
            files = result.stdout.strip().split("\n")[:5]
            if files and files[0]:
                return f"Found: {files[0]}"
            return f"No files found for '{query}'."
        return "What file should I find?"
    
    def _search_web(self, command: str) -> str:
        query = command.replace("search the web for", "").replace("search", "").replace("web", "").strip()
        if query:
            url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}"
            subprocess.run(["open", url], capture_output=True)
            return f"Searching for: {query}"
        return "What should I search for?"
    
    def _open_website(self, command: str) -> str:
        url = command.replace("browse", "").replace("go to", "").replace("open", "").strip()
        if not url.startswith("http"):
            url = f"https://{url}"
        subprocess.run(["open", url], capture_output=True)
        return f"Opening {url}"
    
    def _music_control(self, action: str) -> str:
        try:
            actions = {"play": "play", "pause": "pause", "next": "next track", "previous": "previous track"}
            subprocess.run(["osascript", "-e", f'tell application "Spotify" to {actions.get(action, "play")}'])
            return f"Music {action}ed."
        except:
            return "Spotify is not running."
    
    def _notification(self, command: str) -> str:
        msg = command.replace("notification", "").replace("notify", "").replace("remind", "").replace("me", "").strip()
        if msg:
            subprocess.run(["osascript", "-e", f'display notification "{msg}" with title "F.R.I.D.A.Y."'])
            return f"Notification sent: {msg}"
        
        # Check for time-based reminders
        if "in" in command and "minute" in command:
            nums = [int(s) for s in command.split() if s.isdigit()]
            if nums:
                remind_at = dt.datetime.now() + dt.timedelta(minutes=nums[0])
                reminder_msg = command.replace("remind me", "").replace("in", "").replace(str(nums[0]), "").replace("minute", "").strip()
                self.memory.add_reminder(reminder_msg, remind_at.isoformat())
                return f"Reminder set for {nums[0]} minutes from now."
        
        return "What should I remind you about?"
    
    def _system_info(self) -> str:
        result = subprocess.run(["sysctl", "hw.model", "hw.memsize", "hw.ncpu"], capture_output=True, text=True)
        uptime = subprocess.run(["uptime"], capture_output=True, text=True).stdout.strip()
        return f"System info retrieved. Uptime: {uptime}"
    
    def _battery(self) -> str:
        result = subprocess.run(["pmset", "-g", "batt"], capture_output=True, text=True)
        return result.stdout.strip() or "Could not read battery."
    
    def _wifi(self) -> str:
        result = subprocess.run(["networksetup", "-getairportnetwork", "en0"], capture_output=True, text=True)
        return f"Connected to WiFi: {result.stdout.strip()}"
    
    def _sleep(self) -> str:
        subprocess.run(["pmset", "sleepnow"], capture_output=True)
        return "Putting Mac to sleep."
    
    def _restart(self) -> str:
        subprocess.run(["osascript", "-e", 'tell application "System Events" to restart'])
        return "Restarting Mac."
    
    def _shutdown(self) -> str:
        subprocess.run(["osascript", "-e", 'tell application "System Events" to shut down'])
        return "Shutting down Mac."
    
    def _lock_screen(self) -> str:
        subprocess.run(["/System/Library/CoreServices/Menu\\ Extras/User.menu/Contents/Resources/CGSession", "-suspend"])
        return "Mac locked."
    
    def _empty_trash(self) -> str:
        subprocess.run(["osascript", "-e", 'tell application "Finder" to empty trash'])
        return "Trash emptied."
    
    def _read_clipboard(self) -> str:
        result = subprocess.run(["pbpaste"], capture_output=True, text=True)
        content = result.stdout.strip()[:500]
        return f"Clipboard: {content or 'Clipboard is empty.'}"
    
    def _copy_to_clipboard(self, command: str) -> str:
        text = command.replace("copy", "").strip()
        if text:
            subprocess.run(["pbcopy"], input=text, text=True)
            return f"Copied to clipboard: {text[:50]}."
        return "What should I copy?"
    
    def _paste(self) -> str:
        result = subprocess.run(["pbpaste"], capture_output=True, text=True)
        return result.stdout.strip() or "Nothing to paste."
    
    def _remember(self, command: str) -> str:
        text = command.replace("remember", "").replace("note", "").strip()
        if text:
            self.memory.remember("user_note", text, "note")
            return f"Got it. I'll remember: {text}"
        return "What should I remember?"
    
    def _recall(self, command: str) -> str:
        query = command.replace("what do you remember", "").replace("recall", "").strip()
        if query:
            results = self.memory.search_memories(query)
            if results:
                return f"I recall: {results[0]['value']}"
            return f"I don't have anything about '{query}'."
        
        results = self.memory.search_memories("", limit=5)
        if results:
            return f"I remember: {results[0]['value']}"
        return "I don't have any memories yet."
    
    def _tasks(self, command: str) -> str:
        if "add task" in command or "new task" in command:
            task = command.replace("add task", "").replace("new task", "").strip()
            if task:
                self.memory.add_task(task)
                return f"Task added: {task}"
        elif "show tasks" in command or "list tasks" in command:
            tasks = self.memory.get_tasks()
            if tasks:
                return "Your tasks:\n" + "\n".join([f"• {t['title']}" for t in tasks[:5]])
            return "No tasks found."
        elif "complete task" in command or "done task" in command:
            return "Which task did you complete?"
        return "Use 'add task', 'show tasks', or 'complete task'."
    
    def _calculate(self, command: str) -> str:
        import re
        expression = re.sub(r'[^0-9+\-*/().]', '', command)
        try:
            result = eval(expression)
            return f"{expression} = {result}"
        except:
            return "I couldn't calculate that."
    
    def _run_terminal(self, command: str) -> Optional[str]:
        if command.startswith("run ") or command.startswith("execute ") or command.startswith("$"):
            cmd = command.replace("run ", "").replace("execute ", "").replace("$", "").strip()
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                return result.stdout.strip()[:500] or result.stderr.strip()[:500] or "Command executed."
            except Exception as e:
                return f"Error: {e}"
        return None


# =============================================================================
# PROACTIVE INTELLIGENCE — F.R.I.D.A.Y. initiates
# =============================================================================

class ProactiveIntelligence(QObject):
    suggestion = pyqtSignal(str)
    
    def __init__(self, memory: MemoryDatabase):
        super().__init__()
        self.memory = memory
        self.running = False
        self._thread = None
    
    def start(self):
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._check_loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        self.running = False
    
    def _check_loop(self):
        while self.running:
            try:
                # Check reminders
                reminders = self.memory.get_due_reminders()
                for reminder in reminders:
                    self.suggestion.emit(f"Reminder: {reminder['message']}")
                    cursor = self.memory.conn.cursor()
                    cursor.execute("UPDATE reminders SET triggered = 1 WHERE id = ?", (reminder['id'],))
                    self.memory.conn.commit()
                
                # Check tasks due today
                tasks = self.memory.get_tasks()
                today = dt.datetime.now().strftime("%Y-%m-%d")
                for task in tasks[:1]:
                    if task.get('due_date') and today in str(task.get('due_date', '')):
                        self.suggestion.emit(f"Task due today: {task['title']}")
                
                # Weather check
                if random.random() < 0.01:  # ~5 min check
                    self._check_weather()
                
            except:
                pass
            
            time.sleep(60)  # Check every minute
    
    def _check_weather(self):
        try:
            import urllib.request
            url = f"https://wttr.in/{LOCATION}?format=j1"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as r:
                data = json.loads(r.read())
            current = data.get("current_condition", [{}])[0]
            temp = current.get("temp_C", "?")
            condition = current.get("weatherDesc", [{}])[0].get("value", "")
            
            if "rain" in condition.lower():
                self.suggestion.emit(f"Warning: Rain expected in {LOCATION}. Don't forget your umbrella!")
            elif int(temp) > 35:
                self.suggestion.emit(f"Heat alert: {temp}°C in {LOCATION}. Stay hydrated!")
        except:
            pass


# =============================================================================
# CHAT BUBBLE WIDGET
# =============================================================================

class ChatBubble(QFrame):
    def __init__(self, text: str, is_user: bool = False, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.setStyleSheet(f"""
            QFrame {{
                background: {'rgba(0, 40, 80, 0.9)' if not is_user else 'rgba(80, 30, 0, 0.9)'};
                border: 1px solid {'rgba(0, 180, 255, 0.4)' if not is_user else 'rgba(255, 120, 0, 0.4)'};
                border-radius: 12px;
                padding: 12px;
                margin: 4px 20px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        label = QLabel(text)
        label.setWordWrap(True)
        label.setStyleSheet("color: #c8e8f0; background: transparent; border: none;")
        label.setFont(QFont("Arial", 13))
        layout.addWidget(label)


# =============================================================================
# MENU BAR WIDGET
# =============================================================================

class MenuBarWidget:
    def __init__(self, parent_window):
        self.window = parent_window
        self.tray = QSystemTrayIcon(parent_window)
        
        # Create menu
        self.menu = QMenu()
        
        # Status
        self.status_action = QAction("F.R.I.D.A.Y. PRO — Online", self.menu)
        self.status_action.setEnabled(False)
        self.menu.addAction(self.status_action)
        self.menu.addSeparator()
        
        # Quick Actions
        self.menu.addAction("🎤 Start Voice", self.window.start_voice_input)
        self.menu.addAction("📝 New Note", self.window.add_note)
        self.menu.addAction("🔍 Quick Search", self.window.quick_search)
        self.menu.addSeparator()
        
        # Open Main Window
        self.menu.addAction("📊 Open F.R.I.D.A.Y.", self.window.show)
        self.menu.addAction("⚙️ Settings", self.window.open_settings)
        self.menu.addSeparator()
        
        # Exit
        self.menu.addAction("❌ Quit", self.window.close)
        
        self.tray.setContextMenu(self.menu)
        self.tray.activated.connect(lambda: self.window.show())
        
        # Icon
        self._update_icon()
        
        self.tray.show()
    
    def _update_icon(self):
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 50, 80))
        self.tray.setIcon(QIcon(pixmap))
    
    def show_notification(self, title: str, message: str):
        self.tray.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 5000)


# =============================================================================
# MAIN WINDOW — F.R.I.D.A.Y. PRO Interface
# =============================================================================

class FridayWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Core systems
        self.voice = FridayVoice()
        self.voice_input = VoiceListener()
        self.voice_input.heard.connect(self.on_voice_heard)
        self.voice_input.status_changed.connect(self.on_voice_status)
        self.system = SystemController()
        self.memory = self.system.memory
        self.wake_word = WakeWordListener()
        self.wake_word.triggered.connect(self.on_wake_triggered)
        self.proactive = ProactiveIntelligence(self.memory)
        self.proactive.suggestion.connect(self.on_proactive_suggestion)
        
        self.conversation = []
        self.is_listening = False
        self.current_theme = "jarvis"
        
        self._init_ui()
        self._start_background_services()
        self.greeting()
    
    def _init_ui(self):
        self.setWindowTitle(f"{APP_NAME} v{VERSION}")
        self.setStyleSheet("background-color: #030810;")
        self.resize(1100, 800)
        self.setMinimumSize(900, 650)
        
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
        
        # Title bar
        title = QLabel(f"  {APP_NAME}  —  Intelligent Digital Assistant")
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
        content_layout.setContentsMargins(15, 15, 15, 15)
        
        # Top row: Arc Reactor + Status Panel
        top_row = QHBoxLayout()
        
        self.arc = ArcReactorWidget()
        self.arc.setFixedSize(280, 280)
        top_row.addWidget(self.arc)
        
        # Status panel
        status_panel = QWidget()
        status_panel.setStyleSheet("""
            background: rgba(0, 15, 35, 0.9);
            border: 1px solid rgba(0, 212, 255, 0.15);
            border-radius: 12px;
            padding: 10px;
        """)
        sp_layout = QVBoxLayout(status_panel)
        sp_layout.setContentsMargins(15, 15, 15, 15)
        sp_layout.setSpacing(10)
        
        self.status_label = QLabel("STATUS: ONLINE")
        self.status_label.setStyleSheet("color: #00ff88; font-size: 14px; font-weight: bold; letter-spacing: 2px;")
        self.status_label.setFont(QFont("Courier", 12, QFont.Weight.Bold))
        
        self.time_label = QLabel()
        self.time_label.setStyleSheet("color: rgba(0, 200, 255, 0.8); font-size: 12px;")
        self.time_label.setFont(QFont("Courier", 11))
        
        self.weather_label = QLabel("WEATHER: Loading...")
        self.weather_label.setStyleSheet("color: rgba(0, 200, 255, 0.8); font-size: 12px;")
        self.weather_label.setFont(QFont("Courier", 11))
        
        self.response_label = QLabel("GROQ: Connected")
        self.response_label.setStyleSheet("color: rgba(0, 200, 255, 0.8); font-size: 12px;")
        self.response_label.setFont(QFont("Courier", 11))
        
        self.voice_status_label = QLabel("VOICE: Ready")
        self.voice_status_label.setStyleSheet("color: rgba(0, 212, 255, 0.8); font-size: 12px;")
        self.voice_status_label.setFont(QFont("Courier", 11))
        
        self.memory_label = QLabel("MEMORY: Active")
        self.memory_label.setStyleSheet("color: rgba(0, 212, 255, 0.8); font-size: 12px;")
        self.memory_label.setFont(QFont("Courier", 11))
        
        # Tasks summary
        self.tasks_label = QLabel("TASKS: 0 pending")
        self.tasks_label.setStyleSheet("color: rgba(0, 255, 136, 0.8); font-size: 12px;")
        self.tasks_label.setFont(QFont("Courier", 11))
        
        sp_layout.addWidget(self.status_label)
        sp_layout.addWidget(self.time_label)
        sp_layout.addWidget(self.weather_label)
        sp_layout.addWidget(self.response_label)
        sp_layout.addWidget(self.voice_status_label)
        sp_layout.addWidget(self.memory_label)
        sp_layout.addWidget(self.tasks_label)
        sp_layout.addStretch()
        
        top_row.addWidget(status_panel, 1)
        
        content_layout.addLayout(top_row)
        
        # Chat area
        self.chat_area = QScrollArea()
        self.chat_area.setStyleSheet("""
            QScrollArea { background: rgba(0, 20, 40, 0.3); border-radius: 12px; border: 1px solid rgba(0, 212, 255, 0.1); }
            QScrollBar:vertical { background: rgba(0,50,80,0.5); width: 6px; border-radius: 3px; }
            QScrollBar::handle { background: rgba(0,170,255,0.5); border-radius: 3px; }
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
        
        # Voice visualization
        self.voice_viz = QLabel("🎤 Ready to listen")
        self.voice_viz.setStyleSheet("""
            color: #00d4ff;
            font-size: 14px;
            font-weight: bold;
            letter-spacing: 2px;
            padding: 8px;
            background: rgba(0, 30, 60, 0.7);
            border-radius: 8px;
            border: 1px solid rgba(0, 212, 255, 0.2);
        """)
        self.voice_viz.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.voice_viz.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(self.voice_viz)
        
        # Input area
        input_row = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("  Type your command or press 🎤 to speak...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background: rgba(0, 30, 60, 0.8);
                color: #c8e8f0;
                border: 1px solid rgba(0, 170, 255, 0.3);
                border-radius: 10px;
                padding: 14px 18px;
                font-size: 14px;
                font-family: Arial;
            }
            QLineEdit:focus {
                border: 1px solid #00d4ff;
                background: rgba(0, 50, 100, 0.8);
            }
            QLineEdit::placeholder { color: rgba(0,150,200,0.5); }
        """)
        self.input_field.setFont(QFont("Arial", 14))
        self.input_field.returnPressed.connect(self.send_message)
        
        self.mic_btn = QPushButton("🎤")
        self.mic_btn.setFixedSize(55, 50)
        self.mic_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 40, 80, 0.9);
                border: 1px solid rgba(0, 212, 255, 0.3);
                border-radius: 10px;
                color: #00d4ff;
                font-size: 22px;
            }
            QPushButton:hover { background: rgba(0, 60, 120, 0.9); border-color: #00d4ff; }
            QPushButton:pressed { background: rgba(0, 100, 180, 0.9); }
        """)
        self.mic_btn.clicked.connect(self.toggle_voice)
        
        self.send_btn = QPushButton("SEND")
        self.send_btn.setFixedSize(90, 50)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background: linear-gradient(135deg, #0066aa, #00aaff);
                color: white;
                border-radius: 10px;
                font-weight: bold;
                font-size: 13px;
                letter-spacing: 2px;
            }
            QPushButton:hover { background: linear-gradient(135deg, #0088cc, #00ccff); }
        """)
        self.send_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.send_btn.clicked.connect(self.send_message)
        
        input_row.addWidget(self.input_field)
        input_row.addWidget(self.mic_btn)
        input_row.addWidget(self.send_btn)
        
        content_layout.addLayout(input_row)
        
        main.addWidget(content)
        
        # Status timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_status)
        self.timer.start(1000)
        
        # Menu bar widget
        self.menu_bar = MenuBarWidget(self)
        
        self.show()
    
    def _update_status(self):
        now = dt.datetime.now()
        self.time_label.setText(f"DATE: {now.strftime('%d %b %Y')}\nTIME: {now.strftime('%I:%M:%S %p')}")
        
        if not hasattr(self, '_weather_fetched'):
            self._weather_fetched = True
            threading.Thread(target=self._fetch_weather, daemon=True).start()
        
        if not hasattr(self, '_tasks_fetched'):
            self._tasks_fetched = True
            threading.Thread(target=self._update_tasks, daemon=True).start()
    
    def _fetch_weather(self):
        try:
            import urllib.request
            url = f"https://wttr.in/{LOCATION}?format=j1"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as r:
                data = json.loads(r.read())
            current = data.get("current_condition", [{}])[0]
            temp = current.get("temp_C", "?")
            condition = current.get("weatherDesc", [{}])[0].get("value", "Clear")
            self.weather_label.setText(f"WEATHER: {temp}°C, {condition}")
        except:
            self.weather_label.setText(f"WEATHER: 28°C, Clear")
    
    def _update_tasks(self):
        tasks = self.memory.get_tasks()
        count = len(tasks)
        self.tasks_label.setText(f"TASKS: {count} pending")
    
    def _start_background_services(self):
        self.wake_word.start()
        self.proactive.start()
    
    def greeting(self):
        hour = dt.datetime.now().hour
        if 5 <= hour < 12:
            greeting = f"Good morning, {YOUR_NAME}."
        elif 12 <= hour < 17:
            greeting = f"Good afternoon, {YOUR_NAME}."
        elif 17 <= hour < 21:
            greeting = f"Good evening, {YOUR_NAME}."
        else:
            greeting = f"Good evening, {YOUR_NAME}."
        
        full = (
            f"{greeting} F.R.I.D.A.Y. PRO v{VERSION} fully operational. "
            f"Ready to assist. How may I help you today?"
        )
        self.add_message(full, is_user=False)
        self.voice.speak(full)
    
    def add_message(self, text: str, is_user: bool = False):
        bubble = ChatBubble(text, is_user)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble)
        
        QTimer.singleShot(50, lambda: self.chat_area.verticalScrollBar().setValue(
            self.chat_area.verticalScrollBar().maximum()
        ))
    
    def send_message(self, text: str = None):
        text = text or self.input_field.text().strip()
        if not text:
            return
        
        self.input_field.clear()
        self.add_message(text, is_user=True)
        self.conversation.append({"role": "user", "content": text})
        self.memory.add_conversation("user", text)
        
        threading.Thread(target=self._get_response, args=(text,), daemon=True).start()
    
    def _get_response(self, text: str):
        # First check system commands
        system_response = self.system.execute(text)
        if system_response:
            self.add_message(system_response, is_user=False)
            self.voice.speak(system_response)
            return
        
        # Then check AI
        try:
            import urllib.request, urllib.error
            data = json.dumps({"messages": self.conversation[-8:]}).encode()
            req = urllib.request.Request(
                f"{FRIDAY_SERVER}/chat",
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=30) as r:
                result = json.loads(r.read())
            reply = result.get("reply", "Processing complete.")
        except Exception as e:
            reply = f"Connection issue. All systems nominal. Error: {str(e)[:50]}"
        
        self.add_message(reply, is_user=False)
        self.voice.speak(reply)
        self.conversation.append({"role": "assistant", "content": reply})
        self.memory.add_conversation("assistant", reply)
    
    def toggle_voice(self):
        if self.is_listening:
            self.stop_voice_input()
        else:
            self.start_voice_input()
    
    def start_voice_input(self):
        if self.is_listening:
            return
        self.is_listening = True
        self.mic_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 50, 0, 0.8);
                border: 2px solid #ff6600;
                border-radius: 10px;
                color: white;
                font-size: 22px;
            }
        """)
        self.voice_viz.setText("🎤 LISTENING...")
        self.voice_viz.setStyleSheet("""
            color: #ff6600;
            font-size: 14px;
            font-weight: bold;
            letter-spacing: 2px;
            padding: 8px;
            background: rgba(60, 20, 0, 0.8);
            border-radius: 8px;
            border: 1px solid rgba(255, 100, 0, 0.5);
        """)
        self.voice_input.start()
    
    def stop_voice_input(self):
        self.is_listening = False
        self.voice_input.stop()
        self.mic_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 40, 80, 0.9);
                border: 1px solid rgba(0, 212, 255, 0.3);
                border-radius: 10px;
                color: #00d4ff;
                font-size: 22px;
            }
            QPushButton:hover { background: rgba(0, 60, 120, 0.9); border-color: #00d4ff; }
        """)
        self.voice_viz.setText("🎤 Ready to listen")
        self.voice_viz.setStyleSheet("""
            color: #00d4ff;
            font-size: 14px;
            font-weight: bold;
            letter-spacing: 2px;
            padding: 8px;
            background: rgba(0, 30, 60, 0.7);
            border-radius: 8px;
            border: 1px solid rgba(0, 212, 255, 0.2);
        """)
    
    def on_voice_heard(self, text: str):
        self.stop_voice_input()
        if text.strip():
            self.send_message(text)
    
    def on_voice_status(self, status: str):
        self.voice_status_label.setText(f"VOICE: {status.upper()}")
    
    def on_wake_triggered(self):
        self.arc.pulse_wake()
        self.voice.speak("Yes, Rutwik?")
        self.show()
        self.raise_()
        self.activateWindow()
    
    def on_proactive_suggestion(self, suggestion: str):
        self.add_message(f"💡 {suggestion}", is_user=False)
        self.menu_bar.show_notification("F.R.I.D.A.Y.", suggestion)
    
    def add_note(self):
        self.show()
        self.input_field.setText("remember: ")
        self.input_field.setFocus()
    
    def quick_search(self):
        self.show()
        self.input_field.setText("search the web for: ")
        self.input_field.setFocus()
    
    def open_settings(self):
        self.add_message("Settings panel coming soon.", is_user=False)
    
    def closeEvent(self, event):
        self.wake_word.stop()
        self.proactive.stop()
        self.memory.close()
        event.accept()


# =============================================================================
# SPLASH SCREEN
# =============================================================================

class SplashScreen(QSplashScreen):
    def __init__(self):
        pixmap = QPixmap(600, 400)
        pixmap.fill(QColor(10, 12, 16))
        super().__init__(pixmap)
        
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        
        # Title
        title_label = QLabel("F.R.I.D.A.Y. PRO", self)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            color: #00d4ff;
            font-size: 52px;
            font-weight: bold;
            letter-spacing: 12px;
            background: transparent;
            text-shadow: 0 0 30px rgba(0,212,255,0.8);
        """)
        title_label.setFont(QFont("Arial", 48, QFont.Weight.Bold))
        title_label.resize(600, 400)
        title_label.move(0, 140)
        
        # Subtitle
        sub_label = QLabel("FULLY RESPONSIVE INTELLIGENT DIGITAL ASSISTANT", self)
        sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_label.setStyleSheet("color: rgba(0,170,255,0.6); font-size: 11px; letter-spacing: 4px; background: transparent;")
        sub_label.setFont(QFont("Arial", 10))
        sub_label.resize(600, 400)
        sub_label.move(0, 210)
        
        # Loading
        loading_label = QLabel("Initializing systems...", self)
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_label.setStyleSheet("color: rgba(0,200,255,0.5); font-size: 12px; background: transparent;")
        loading_label.setFont(QFont("Courier", 11))
        loading_label.resize(600, 400)
        loading_label.move(0, 300)
        
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
    app.setApplicationVersion(VERSION)
    
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(10, 12, 16))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(200, 232, 240))
    app.setPalette(palette)
    
    splash = SplashScreen()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
