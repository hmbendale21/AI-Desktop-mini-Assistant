import sys
import os
import math
import datetime

# Suppress Qt DPI environment log warning
os.environ["QT_LOGGING_RULES"] = "qt.qpa.window.warning=false"

from PySide6.QtCore import Qt, QThread, Signal, Slot, QTimer
from PySide6.QtGui import QFont, QColor, QPainter, QPainterPath, QPen, QBrush
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QLineEdit, QComboBox,
    QDialog, QFrame, QGridLayout
)




from config import ConfigManager
from voice_engine import VoiceEngine
from pc_controller import PCController


class AudioWaveVisualizer(QWidget):
    """Animated glowing audio wave visualizer for speech input."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(80)
        self.phase = 0.0
        self.is_active = False
        self.mode = "idle"  # idle, listening, processing, speaking
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_wave)
        self.timer.start(30)

    def set_state(self, mode: str):
        self.mode = mode
        self.is_active = mode in ["listening", "processing", "speaking"]

    def update_wave(self):
        if self.is_active:
            self.phase += 0.15
        else:
            self.phase += 0.03
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        cy = h / 2.0

        # Background fill
        painter.fillRect(0, 0, w, h, QColor(20, 24, 38))

        if self.mode == "listening":
            color_primary = QColor(0, 210, 255, 220)    # Cyan
            color_secondary = QColor(127, 0, 255, 140)  # Purple
            amplitude = 25.0
            freq = 0.03
        elif self.mode == "processing":
            color_primary = QColor(255, 170, 0, 220)   # Orange/Gold
            color_secondary = QColor(255, 0, 128, 140)  # Pink
            amplitude = 15.0
            freq = 0.08
        elif self.mode == "speaking":
            color_primary = QColor(0, 230, 118, 220)   # Emerald
            color_secondary = QColor(0, 176, 255, 140)  # Teal
            amplitude = 20.0
            freq = 0.04
        else:
            color_primary = QColor(80, 95, 130, 100)
            color_secondary = QColor(40, 50, 80, 80)
            amplitude = 4.0
            freq = 0.02

        # Draw secondary background wave
        path_sec = QPainterPath()
        path_sec.moveTo(0, cy)
        for x in range(0, w, 4):
            y = cy + math.sin(x * freq * 0.7 - self.phase) * (amplitude * 0.6)
            path_sec.lineTo(x, y)
        path_sec.lineTo(w, h)
        path_sec.lineTo(0, h)
        painter.fillPath(path_sec, QBrush(color_secondary))

        # Draw primary foreground line wave
        path_pri = QPainterPath()
        path_pri.moveTo(0, cy)
        for x in range(0, w, 2):
            y = cy + math.sin(x * freq + self.phase) * amplitude * math.sin(x * math.pi / w)
            path_pri.lineTo(x, y)

        pen = QPen(color_primary, 3)
        painter.setPen(pen)
        painter.drawPath(path_pri)


class VoiceWorker(QThread):
    """Background worker thread for speech listening and processing."""
    status_signal = Signal(str, str)  # status_msg, mode
    transcript_signal = Signal(str)
    response_signal = Signal(str)

    def __init__(self, voice_engine: VoiceEngine):
        super().__init__()
        self.engine = voice_engine
        self.running = True

    def run(self):
        while self.running:
            self.status_signal.emit("Listening...", "listening")
            audio, msg = self.engine.listen_audio_data(timeout=7, phrase_time_limit=15)
            
            if not self.running:
                break

            if not audio:
                self.status_signal.emit(msg, "idle")
                continue

            self.status_signal.emit("Transcribing Audio with API...", "processing")
            transcript = self.engine.transcribe(audio)
            
            if not self.running:
                break

            if not transcript:
                self.status_signal.emit("Could not understand audio. Try again.", "idle")
                continue

            self.transcript_signal.emit(transcript)

            self.status_signal.emit("Processing Command...", "processing")
            result = self.engine.process_command(transcript)
            
            if not self.running:
                break

            self.response_signal.emit(result)
            self.status_signal.emit("Speaking Response...", "speaking")
            self.engine.speak(result)
            
            self.status_signal.emit("Ready", "idle")


class SettingsDialog(QDialog):
    """Modal dialog for API key entry and app preferences."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI Assistant Settings & API Keys")
        self.setFixedSize(500, 420)
        self.setStyleSheet("""
            QDialog {
                background-color: #171b26;
                color: #e0e6ed;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #b0b8c8;
                font-size: 13px;
                font-weight: bold;
            }
            QLineEdit, QComboBox {
                background-color: #222838;
                border: 1px solid #343d54;
                border-radius: 6px;
                padding: 8px;
                color: #ffffff;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #00d2ff;
            }
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00c6ff, stop:1 #0072ff);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00d2ff, stop:1 #0088ff);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("⚙️ API Keys & Engine Configuration")
        title.setStyleSheet("font-size: 16px; color: #00d2ff; margin-bottom: 8px;")
        layout.addWidget(title)

        # Gemini Key
        layout.addWidget(QLabel("Google Gemini API Key:"))
        self.gemini_input = QLineEdit()
        self.gemini_input.setEchoMode(QLineEdit.Password)
        self.gemini_input.setText(ConfigManager.get("GEMINI_API_KEY"))
        self.gemini_input.setPlaceholderText("Paste AIZA... Gemini API Key here")
        layout.addWidget(self.gemini_input)

        # OpenAI Key
        layout.addWidget(QLabel("OpenAI API Key (Whisper):"))
        self.openai_input = QLineEdit()
        self.openai_input.setEchoMode(QLineEdit.Password)
        self.openai_input.setText(ConfigManager.get("OPENAI_API_KEY"))
        self.openai_input.setPlaceholderText("Paste sk-... OpenAI API Key here")
        layout.addWidget(self.openai_input)

        # Groq Key
        layout.addWidget(QLabel("Groq API Key (Ultra-fast Whisper):"))
        self.groq_input = QLineEdit()
        self.groq_input.setEchoMode(QLineEdit.Password)
        self.groq_input.setText(ConfigManager.get("GROQ_API_KEY"))
        self.groq_input.setPlaceholderText("Paste gsk_... Groq API Key here")
        layout.addWidget(self.groq_input)

        # Provider Selector
        layout.addWidget(QLabel("Preferred Speech-to-Text Engine:"))
        self.provider_combo = QComboBox()
        self.provider_combo.addItems([
            "Auto (Select best available API Key)",
            "Gemini Audio STT",
            "OpenAI Whisper API",
            "Groq Whisper API",
            "Google Web STT (No API Key)"
        ])
        current_p = ConfigManager.get("STT_PROVIDER", "auto").lower()
        provider_index_map = {"auto": 0, "gemini": 1, "openai": 2, "groq": 3, "google_web": 4}
        self.provider_combo.setCurrentIndex(provider_index_map.get(current_p, 0))
        layout.addWidget(self.provider_combo)

        # Save Button
        save_btn = QPushButton("Save Settings & Apply")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

    def save_settings(self):
        ConfigManager.set("GEMINI_API_KEY", self.gemini_input.text().strip())
        ConfigManager.set("OPENAI_API_KEY", self.openai_input.text().strip())
        ConfigManager.set("GROQ_API_KEY", self.groq_input.text().strip())

        combo_map = {0: "auto", 1: "gemini", 2: "openai", 3: "groq", 4: "google_web"}
        selected_provider = combo_map.get(self.provider_combo.currentIndex(), "auto")
        ConfigManager.set("STT_PROVIDER", selected_provider)

        self.accept()


class MainWindow(QMainWindow):
    """Main Desktop Voice Assistant Window."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Desktop Voice Assistant - PC Control")
        self.resize(920, 680)
        
        self.voice_engine = VoiceEngine()
        self.worker = None

        self.init_ui()
        self.update_provider_badge()

    def init_ui(self):
        # Global Window Style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f121d;
                font-family: 'Segoe UI', Roboto, sans-serif;
            }
            QFrame {
                background-color: #171b28;
                border-radius: 12px;
                border: 1px solid #232a3d;
            }
            QLabel {
                color: #e0e6ed;
            }
            QPushButton {
                background-color: #21283c;
                color: #d8e2ef;
                border: 1px solid #2e3852;
                border-radius: 8px;
                padding: 8px 14px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #2d3752;
                border-color: #00d2ff;
                color: #ffffff;
            }
            QTextEdit {
                background-color: #131724;
                color: #a0aec0;
                border: 1px solid #232a3d;
                border-radius: 8px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                padding: 8px;
            }
            QLineEdit {
                background-color: #1a2030;
                border: 1px solid #2c364f;
                border-radius: 8px;
                padding: 10px;
                color: #ffffff;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #00d2ff;
            }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(14)

        # 1. Header Bar
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(14, 10, 14, 10)

        app_title = QLabel("🎙️ AI PC VOICE ASSISTANT")
        app_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        app_title.setStyleSheet("color: #00d2ff; letter-spacing: 1px;")

        self.provider_badge = QLabel("⚡ API: NONE (Web STT)")
        self.provider_badge.setStyleSheet("""
            background-color: #242c40;
            color: #00e676;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
        """)

        settings_btn = QPushButton("⚙️ Settings & API Key")
        settings_btn.clicked.connect(self.open_settings)

        header_layout.addWidget(app_title)
        header_layout.addStretch()
        header_layout.addWidget(self.provider_badge)
        header_layout.addWidget(settings_btn)

        main_layout.addWidget(header_frame)

        # 2. Wave Visualizer & Status Badge
        self.wave_visualizer = AudioWaveVisualizer()
        main_layout.addWidget(self.wave_visualizer)

        self.status_label = QLabel("Click 'START LISTENING' or type a command below")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #94a3b8; font-size: 13px; font-weight: 500;")
        main_layout.addWidget(self.status_label)

        # 3. Main Content Split: Transcripts + Quick Action Buttons
        content_layout = QHBoxLayout()
        content_layout.setSpacing(14)

        # Left Column: User Transcript & Assistant Response
        left_col = QVBoxLayout()
        left_col.setSpacing(10)

        # User Speech Card
        user_card = QFrame()
        user_layout = QVBoxLayout(user_card)
        user_layout.setContentsMargins(12, 10, 12, 10)
        u_lbl = QLabel("🗣️ YOU SAID:")
        u_lbl.setStyleSheet("color: #38bdf8; font-size: 11px; font-weight: bold;")
        self.user_transcript = QLabel("...")
        self.user_transcript.setWordWrap(True)
        self.user_transcript.setFont(QFont("Segoe UI", 13))
        user_layout.addWidget(u_lbl)
        user_layout.addWidget(self.user_transcript)
        left_col.addWidget(user_card)

        # AI Response Card
        ai_card = QFrame()
        ai_layout = QVBoxLayout(ai_card)
        ai_layout.setContentsMargins(12, 10, 12, 10)
        ai_lbl = QLabel("🤖 ASSISTANT RESPONSE:")
        ai_lbl.setStyleSheet("color: #4ade80; font-size: 11px; font-weight: bold;")
        self.ai_response = QLabel("Ready to assist you.")
        self.ai_response.setWordWrap(True)
        self.ai_response.setFont(QFont("Segoe UI", 13))
        ai_layout.addWidget(ai_lbl)
        ai_layout.addWidget(self.ai_response)
        left_col.addWidget(ai_card)

        # Activity Log
        log_lbl = QLabel("📜 Activity & Execution Log")
        log_lbl.setStyleSheet("color: #64748b; font-size: 12px; font-weight: bold;")
        left_col.addWidget(log_lbl)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        left_col.addWidget(self.log_box, stretch=1)

        content_layout.addLayout(left_col, stretch=6)

        # Right Column: Quick Action Grid
        right_card = QFrame()
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(12, 12, 12, 12)

        qa_lbl = QLabel("⚡ Quick Actions")
        qa_lbl.setStyleSheet("color: #f43f5e; font-size: 13px; font-weight: bold; margin-bottom: 4px;")
        right_layout.addWidget(qa_lbl)

        grid = QGridLayout()
        grid.setSpacing(8)

        actions = [
            ("📸 Screenshot", lambda: self.execute_text_command("take screenshot")),
            ("🔊 Vol Up", lambda: self.execute_text_command("volume up")),
            ("🔉 Vol Down", lambda: self.execute_text_command("volume down")),
            ("📝 Notepad", lambda: self.execute_text_command("open notepad")),
            ("💻 CMD", lambda: self.execute_text_command("open cmd")),
            ("⚡ CPU Usage", lambda: self.execute_text_command("check cpu usage")),
            ("🌐 YouTube", lambda: self.execute_text_command("open youtube")),
            ("🧮 Calculator", lambda: self.execute_text_command("open calculator")),
            ("🌐 IP Address", lambda: self.execute_text_command("check ip address")),
            ("🗑️ Recycle Bin", lambda: self.execute_text_command("empty recycle bin")),
        ]

        for idx, (label, func) in enumerate(actions):
            btn = QPushButton(label)
            btn.clicked.connect(func)
            grid.addWidget(btn, idx // 2, idx % 2)

        right_layout.addLayout(grid)
        right_layout.addStretch()

        content_layout.addWidget(right_card, stretch=4)
        main_layout.addLayout(content_layout, stretch=1)

        # 4. Bottom Controls: Push to Talk & Manual Text Command
        ctrl_frame = QFrame()
        ctrl_layout = QHBoxLayout(ctrl_frame)
        ctrl_layout.setContentsMargins(12, 10, 12, 10)

        self.listen_btn = QPushButton("🎤 START LISTENING")
        self.listen_btn.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00c6ff, stop:1 #0072ff);
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00d2ff, stop:1 #0088ff);
            }
        """)
        self.listen_btn.clicked.connect(self.start_listening)

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Type a command here (e.g. 'open google', 'take screenshot', 'calculate 25 * 4')...")
        self.text_input.returnPressed.connect(self.handle_text_submit)

        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.handle_text_submit)

        ctrl_layout.addWidget(self.listen_btn)
        ctrl_layout.addWidget(self.text_input, stretch=1)
        ctrl_layout.addWidget(send_btn)

        main_layout.addWidget(ctrl_frame)

        # Initial Welcome Speech
        self.log_event("Application initialized.")
        self.voice_engine.speak("Good day! Ready to comply. How can I assist you?")

    def open_settings(self):
        dlg = SettingsDialog(self)
        if dlg.exec() == QDialog.Accepted:
            self.update_provider_badge()
            self.log_event("Updated settings & API Key configuration.")

    def update_provider_badge(self):
        provider, key = ConfigManager.get_api_key()
        if provider == "gemini":
            self.provider_badge.setText("⚡ API: GEMINI AUDIO")
            self.provider_badge.setStyleSheet("background-color: #1e3a8a; color: #60a5fa; padding: 4px 12px; border-radius: 12px; font-weight: bold;")
        elif provider == "openai":
            self.provider_badge.setText("⚡ API: OPENAI WHISPER")
            self.provider_badge.setStyleSheet("background-color: #065f46; color: #34d399; padding: 4px 12px; border-radius: 12px; font-weight: bold;")
        elif provider == "groq":
            self.provider_badge.setText("⚡ API: GROQ WHISPER")
            self.provider_badge.setStyleSheet("background-color: #831843; color: #f472b6; padding: 4px 12px; border-radius: 12px; font-weight: bold;")
        else:
            self.provider_badge.setText("🌐 GOOGLE WEB STT (No Key)")
            self.provider_badge.setStyleSheet("background-color: #334155; color: #94a3b8; padding: 4px 12px; border-radius: 12px; font-weight: bold;")

    def start_listening(self):
        if self.worker and self.worker.isRunning():
            self.worker.running = False
            self.listen_btn.setText("Stopping...")
            self.listen_btn.setEnabled(False)
            return
        
        self.listen_btn.setText("🛑 STOP LISTENING")
        self.listen_btn.setStyleSheet("""
            QPushButton {
                background-color: #f03e3e;
                color: white;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c92a2a;
            }
        """)
        
        self.worker = VoiceWorker(self.voice_engine)
        self.worker.status_signal.connect(self.on_voice_status)
        self.worker.transcript_signal.connect(self.on_user_transcript)
        self.worker.response_signal.connect(self.on_ai_response)
        self.worker.finished.connect(self.on_voice_finished)
        self.worker.start()

    @Slot(str, str)
    def on_voice_status(self, status_msg, mode):
        self.status_label.setText(status_msg)
        self.wave_visualizer.set_state(mode)

    @Slot(str)
    def on_user_transcript(self, text):
        self.user_transcript.setText(text)
        self.log_event(f"User Spoke: '{text}'")

    @Slot(str)
    def on_ai_response(self, text):
        self.ai_response.setText(text)
        self.log_event(f"Action Output: {text}")

    def on_voice_finished(self):
        self.listen_btn.setEnabled(True)
        self.listen_btn.setText("🎤 START LISTENING")
        self.listen_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        self.status_label.setText("Ready")
        self.wave_visualizer.set_state("idle")

    def handle_text_submit(self):
        cmd = self.text_input.text().strip()
        if cmd:
            self.text_input.clear()
            self.execute_text_command(cmd)

    def execute_text_command(self, cmd: str):
        self.user_transcript.setText(cmd)
        self.log_event(f"Manual Command: '{cmd}'")
        self.wave_visualizer.set_state("processing")
        self.status_label.setText("Processing Command...")
        
        QApplication.processEvents()
        
        result = self.voice_engine.process_command(cmd)
        
        self.ai_response.setText(result)
        self.log_event(f"Action Output: {result}")
        self.wave_visualizer.set_state("speaking")
        self.status_label.setText("Speaking Response...")
        
        QApplication.processEvents()
        self.voice_engine.speak(result)
        
        self.wave_visualizer.set_state("idle")
        self.status_label.setText("Ready")

    def log_event(self, msg: str):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_box.append(f"[{timestamp}] {msg}")


def launch_gui():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    launch_gui()
