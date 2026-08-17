# 🎙️ AI Desktop Mini Assistant

An intelligent **AI-powered desktop voice assistant** built with Python that allows users to interact with their Windows PC using natural voice commands.

The assistant combines **speech recognition, AI-based intent processing, text-to-speech, and Windows PC automation** in a modern PySide6 graphical interface.

## ✨ Features

* 🎤 Voice-based command recognition
* 🤖 AI intent processing using Google Gemini
* 🗣️ Text-to-Speech responses using `pyttsx3`
* ⚡ Multiple Speech-to-Text providers:

  * Groq Whisper
  * OpenAI Whisper
  * Google Gemini
  * Google Web Speech Recognition
* 🖥️ Windows application control
* 🔊 Volume control and mute
* 💡 Screen brightness control
* 📸 Screenshot capture
* 🎥 Screen recording
* 📷 Webcam access
* 🌐 Google and YouTube search
* 📚 Wikipedia information search
* 🧮 Voice-based calculations
* 💻 CPU, RAM and battery monitoring
* 📁 Create and delete desktop folders
* 🔄 Refresh desktop
* 🔐 System lock, sleep, restart and shutdown
* 💬 WhatsApp message automation
* 🎨 Animated voice-wave GUI
* ⚙️ Built-in API key and speech-engine settings

The PC automation layer handles application launching, system controls, screenshots, recording, monitoring and other utilities.

## 🛠️ Technologies Used

* **Python**
* **PySide6** – Desktop GUI
* **SpeechRecognition** – Speech input
* **pyttsx3** – Text-to-Speech
* **Google Gemini API** – AI intent processing / audio processing
* **OpenAI Whisper API** – Speech-to-Text
* **Groq Whisper API** – Fast Speech-to-Text
* **PyAutoGUI** – Desktop automation
* **OpenCV** – Camera and screen processing
* **PyAudio / Microphone input**
* **psutil** – System monitoring
* **WMI** – Windows brightness control
* **PyWhatKit** – WhatsApp / YouTube automation
* **Wikipedia API**
* **python-dotenv** – Configuration management

## 📂 Project Structure

```text
AI-Desktop-mini-Assistant/
│
├── main.py              # Application entry point / CLI mode
├── app_gui.py            # PySide6 graphical interface
├── voice_engine.py       # Speech recognition, AI processing & TTS
├── pc_controller.py      # Windows PC automation
├── config.py             # API key and configuration management
├── .gitignore
└── README.md
```

`main.py` launches the GUI by default and also supports a CLI mode using `--cli`.

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/hmbendale21/AI-Desktop-mini-Assistant-.git
cd AI-Desktop-mini-Assistant-
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install PySide6 SpeechRecognition pyttsx3 requests python-dotenv
pip install pyautogui psutil WMI pywhatkit wikipedia opencv-python numpy pillow
```

### 4. Run the assistant

```bash
python main.py
```

For CLI mode:

```bash
python main.py --cli
```

## 🔑 API Configuration

The application supports configuration for:

* `GEMINI_API_KEY`
* `OPENAI_API_KEY`
* `GROQ_API_KEY`
* `STT_PROVIDER`
* `TTS_SPEED`

The GUI provides a dedicated **Settings & API Key** window where API keys and the preferred speech-to-text provider can be configured.

The configuration is stored through a `.env` file.

> ⚠️ Never upload your `.env` file or expose API keys publicly.

## 🎯 Example Voice Commands

```text
"Open Chrome"
"Open VS Code"
"Increase volume"
"Decrease brightness"
"Take screenshot"
"Record screen"
"Open camera"
"Check CPU"
"Check battery"
"What is Artificial Intelligence?"
"Search Google for Python"
"Play music"
"Calculate 25 plus 15"
"Create folder Projects"
"Lock the system"
"Restart the system"
"Shutdown the system"
```

## 🔄 How It Works

```text
Voice Input
     ↓
Speech Recognition
     ↓
AI Intent Processing
     ↓
Command Classification
     ↓
PC Controller
     ↓
Windows Action
     ↓
Voice Response
```

When Gemini is available, the assistant can interpret incomplete or loosely phrased commands and map them to predefined desktop actions; otherwise, it uses a local keyword-based command parser.

## 👨‍💻 Author
**Himanshu Bendale**

GitHub: [@hmbendale21](https://github.com/hmbendale21)

---

⭐ If you find this project useful, consider giving it a star!
