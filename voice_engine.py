import os
import io
import json
import wave
import tempfile
import requests
import pyttsx3
import speech_recognition as sr
from config import ConfigManager
from pc_controller import PCController

import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")
warnings.filterwarnings("ignore", category=UserWarning)

# Try importing google.genai or google.generativeai
try:
    from google import genai
    HAS_GENAI_NEW = True
except ImportError:
    HAS_GENAI_NEW = False

if not HAS_GENAI_NEW:
    try:
        import google.generativeai as genai_legacy
        HAS_GENAI_LEGACY = True
    except ImportError:
        HAS_GENAI_LEGACY = False
else:
    HAS_GENAI_LEGACY = False



class TTSEngine:
    """Thread-safe text-to-speech engine wrapper."""
    def __init__(self):
        self.engine = None
        self._init_engine()

    def _init_engine(self):
        try:
            self.engine = pyttsx3.init('sapi5')
            voices = self.engine.getProperty('voices')
            if voices:
                self.engine.setProperty('voice', voices[0].id)
            speed = int(ConfigManager.get("TTS_SPEED", "150"))
            self.engine.setProperty('rate', speed)
        except Exception:
            try:
                self.engine = pyttsx3.init()
            except Exception:
                self.engine = None

    def speak(self, text: str):
        if not text or not self.engine:
            return
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception:
            # Re-init if engine state was disrupted
            self._init_engine()
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception:
                pass


class VoiceEngine:
    """Speech Recognition and AI Intent Processing Engine."""
    def __init__(self):
        self.tts = TTSEngine()

    def speak(self, text: str):
        self.tts.speak(text)

    def listen_audio_data(self, timeout=10, phrase_time_limit=15) -> tuple[sr.AudioData | None, str]:
        """Captures microphone audio with noise filtering and extended pause threshold."""
        r = sr.Recognizer()
        r.pause_threshold = 1.8  # Wait 1.8 seconds of silence before finishing phrase
        r.non_speaking_duration = 0.8
        r.energy_threshold = 400
        r.dynamic_energy_threshold = True
        r.dynamic_energy_adjustment_ratio = 1.5

        try:
            with sr.Microphone() as source:
                # Calibrate and filter out background PC/room ambient noise
                r.adjust_for_ambient_noise(source, duration=1.0)
                audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                return audio, "Captured audio successfully"
        except sr.WaitTimeoutError:
            return None, "Listening timed out. No speech detected."
        except Exception as e:
            return None, f"Microphone error: {e}"


    def transcribe(self, audio_data: sr.AudioData) -> str:
        """Transcribes audio using API Key (Groq Whisper / Gemini) or Web Google STT fallback."""
        provider, api_key = ConfigManager.get_api_key()
        groq_key = ConfigManager.get("GROQ_API_KEY")
        openai_key = ConfigManager.get("OPENAI_API_KEY")

        # 1. Groq Whisper API (Preferred for STT: Fast, Accurate, No Rate Limits)
        active_groq_key = groq_key or (api_key if provider == "groq" else "")
        if active_groq_key:
            try:
                wav_data = audio_data.get_wav_data()
                files = {"file": ("audio.wav", wav_data, "audio/wav")}
                data = {"model": "whisper-large-v3-turbo"}
                headers = {"Authorization": f"Bearer {active_groq_key}"}
                resp = requests.post("https://api.groq.com/openai/v1/audio/transcriptions", headers=headers, files=files, data=data, timeout=8)
                if resp.status_code == 200:
                    text = resp.json().get("text", "").strip()
                    if text:
                        return text
            except Exception as e:
                print(f"Groq STT Error: {e}")

        # 2. OpenAI Whisper API
        if openai_key:
            try:
                wav_data = audio_data.get_wav_data()
                files = {"file": ("audio.wav", wav_data, "audio/wav")}
                data = {"model": "whisper-1"}
                headers = {"Authorization": f"Bearer {openai_key}"}
                resp = requests.post("https://api.openai.com/v1/audio/transcriptions", headers=headers, files=files, data=data, timeout=8)
                if resp.status_code == 200:
                    text = resp.json().get("text", "").strip()
                    if text:
                        return text
            except Exception as e:
                print(f"OpenAI STT Error: {e}")

        # 3. Gemini Multimodal Audio STT (Fallback)
        if provider == "gemini" and api_key:
            try:
                wav_data = audio_data.get_wav_data()
                if HAS_GENAI_NEW:
                    client = genai.Client(api_key=api_key)
                    response = client.models.generate_content(
                        model="gemini-1.5-flash",
                        contents=[
                            "Transcribe the following user spoken audio accurately. Output only verbatim transcript text.",
                            genai.types.Part.from_bytes(data=wav_data, mime_type="audio/wav")
                        ]
                    )
                    if response.text:
                        return response.text.strip()
                elif HAS_GENAI_LEGACY:
                    genai_legacy.configure(api_key=api_key)
                    model = genai_legacy.GenerativeModel("gemini-1.5-flash")
                    response = model.generate_content([
                        "Transcribe the following spoken audio accurately.",
                        {"mime_type": "audio/wav", "data": wav_data}
                    ])
                    if response.text:
                        return response.text.strip()
            except Exception as e:
                print(f"Gemini STT Rate Limit/Error (falling back to Web STT): {e}")

        # Fallback: Google Free Web STT
        try:
            r = sr.Recognizer()
            return r.recognize_google(audio_data, language="en-US")
        except sr.UnknownValueError:
            return ""
        except Exception as e:
            print(f"Google Web STT error: {e}")
            return ""


    def process_command(self, query: str) -> str:
        """Parses the user transcript and executes the matching desktop action."""
        if not query or query.lower() in ["none", ""]:
            return "Pardon? I didn't catch that."

        q = query.lower().strip()

        # Check if LLM intent parser is available with API key
        provider, api_key = ConfigManager.get_api_key()
        if api_key and provider == "gemini":
            try:
                llm_response = self._parse_intent_with_llm(query, api_key)
                if llm_response:
                    return llm_response
            except Exception as e:
                print(f"LLM intent error: {e}")

        # Local Keyword Parser Fallback (matches all main.py rules & incomplete phrases)
        if "who are you" in q:
            return "I am your AI Desktop Assistant created to help you control your PC using voice."
        elif "who created you" in q:
            return "I was created using Python, PySide6, and AI API models."
        elif "time" in q or "clock" in q:
            t = PCController.get_time()
            return f"Sir, the current time is {t}"
        elif "ip address" in q or "my ip" in q:
            ip = PCController.get_ip()
            return f"Your IP address is {ip}"
        elif "screenshot" in q or "screen shot" in q or "screen cap" in q or "take screen" in q:
            return PCController.take_screenshot()
        elif "screen recording" in q or "record screen" in q or "start rec" in q:
            return PCController.record_screen()
        elif "open camera" in q or "webcam" in q or "open cam" in q:
            return PCController.open_camera()
        elif "volume up" in q or "increase volume" in q or "vol up" in q or "sound up" in q or "louder" in q:
            return PCController.volume_control("up")
        elif "volume down" in q or "decrease volume" in q or "vol down" in q or "sound down" in q or "quieter" in q:
            return PCController.volume_control("down")
        elif "mute" in q or "unmute" in q:
            return PCController.volume_control("mute")
        elif "increase brightness" in q or "brightness up" in q or "bright up" in q:
            return PCController.set_brightness(+15)
        elif "decrease brightness" in q or "brightness down" in q or "bright down" in q:
            return PCController.set_brightness(-15)
        elif "calculate" in q or "plus" in q or "minus" in q or "divided" in q or "times" in q or "multiply" in q:
            clean_math = q.replace("calculate", "").replace("calc", "").strip()
            return PCController.calculate(clean_math)
        elif "joke" in q:
            return PCController.get_joke()
        elif "cpu" in q or "processor" in q:
            return PCController.check_system("cpu")
        elif "memory" in q or "ram" in q or "mem" in q:
            return PCController.check_system("memory")
        elif "battery" in q or "bat" in q or "charge" in q:
            return PCController.check_system("battery")
        elif "recycle bin" in q or "empty bin" in q or "recycle" in q:
            return PCController.empty_recycle_bin()
        elif "open google" in q:
            query_str = q.replace("open google", "").strip()
            PCController.open_google(query_str)
            return "Opening Google"
        elif "open youtube" in q or "play" in q and "youtube" in q:
            query_str = q.replace("open youtube", "").replace("search on youtube", "").replace("play", "").strip()
            return PCController.open_youtube(query_str)
        elif "what is" in q or "who is" in q:
            return PCController.search_wikipedia(q)
        elif "open notepad" in q:
            return PCController.open_application("notepad")
        elif "close notepad" in q:
            return PCController.close_application("notepad")
        elif "open command prompt" in q or "open cmd" in q:
            return PCController.open_application("cmd")
        elif "close command prompt" in q or "close cmd" in q:
            return PCController.close_application("cmd")
        elif "open word" in q:
            return PCController.open_application("word")
        elif "close word" in q:
            return PCController.close_application("word")
        elif "open excel" in q:
            return PCController.open_application("excel")
        elif "close excel" in q:
            return PCController.close_application("excel")
        elif "open powerpoint" in q:
            return PCController.open_application("powerpoint")
        elif "close powerpoint" in q:
            return PCController.close_application("powerpoint")
        elif "open vlc" in q:
            return PCController.open_application("vlc")
        elif "close vlc" in q:
            return PCController.close_application("vlc")
        elif "open code" in q or "open vs code" in q or "open visual" in q or "open vs" in q:
            return PCController.open_application("vs code")
        elif "close code" in q or "close vs code" in q or "close visual" in q:
            return PCController.close_application("vs code")
        elif "open chrome" in q or "open google chrome" in q:
            return PCController.open_application("chrome")
        elif "close chrome" in q:
            return PCController.close_application("chrome")
        elif "create folder" in q:
            name = q.replace("create folder", "").replace("named", "").strip()
            if not name:
                name = "New Folder"
            return PCController.create_desktop_folder(name)
        elif "delete folder" in q:
            name = q.replace("delete folder", "").replace("named", "").strip()
            return PCController.delete_desktop_folder(name)
        elif "refresh" in q:
            return PCController.refresh_desktop()
        elif "spiral" in q or "paint" in q and "rectangular" in q:
            return PCController.draw_spiral()
        elif "shutdown" in q:
            return PCController.system_power("shutdown")

        elif "restart" in q:
            return PCController.system_power("restart")
        elif "lock" in q:
            return PCController.system_power("lock")
        elif "sleep" in q:
            return PCController.system_power("sleep")

        # Generic open/close for partial app names
        if q.startswith("open "):
            app = q.replace("open ", "").strip()
            return PCController.open_application(app)
        if q.startswith("close "):
            app = q.replace("close ", "").strip()
            return PCController.close_application(app)

        return f"Executed command: '{query}'"

    def _parse_intent_with_llm(self, query: str, api_key: str) -> str | None:
        """Uses Gemini API to interpret query and map to PC action even if input is incomplete/partial."""
        prompt = f"""You are an intelligent AI desktop command router.
The user spoken transcript may be incomplete, cut off, contain background noise, or loosely phrased.
User said: "{query}"

Your task: Infer the user's exact true intent even if the message is incomplete or fuzzy.

Examples of incomplete input resolution:
- "open visual..." / "open vs..." -> OPEN_APP (param: "vs code")
- "take screen..." / "screenshot..." -> SCREENSHOT
- "vol up..." / "turn up sound..." -> VOLUME_UP
- "check cpu..." / "cpu usage..." -> SYSTEM_CHECK (param: "cpu")
- "calculate 25 plus..." -> CALCULATE (param: "25 + ")

Available actions:
- GET_TIME
- GET_IP
- SEARCH_WIKI (param: query)
- OPEN_GOOGLE (param: search_term)
- OPEN_YOUTUBE (param: search_term)
- VOLUME_UP
- VOLUME_DOWN
- MUTE
- BRIGHTNESS_UP
- BRIGHTNESS_DOWN
- SCREENSHOT
- RECORD_SCREEN
- OPEN_CAM
- OPEN_APP (param: app_name)
- CLOSE_APP (param: app_name)
- CALCULATE (param: math_expr)
- JOKE
- SYSTEM_CHECK (param: cpu|memory|battery)
- POWER (param: shutdown|restart|lock|sleep)
- EMPTY_RECYCLE_BIN
- CREATE_FOLDER (param: folder_name)
- REFRESH
- DRAW_SPIRAL
- GENERAL_TALK (param: response_text)

Respond ONLY with valid JSON:
{{"action": "ACTION_NAME", "param": "value", "response": "Spoken text response"}}
"""

        try:
            if HAS_GENAI_NEW:
                client = genai.Client(api_key=api_key)
                res = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
                data_text = res.text

            elif HAS_GENAI_LEGACY:
                genai_legacy.configure(api_key=api_key)
                m = genai_legacy.GenerativeModel("gemini-1.5-flash")
                res = m.generate_content(prompt)
                data_text = res.text
            else:
                return None

            # Clean JSON formatting
            data_text = data_text.strip()
            if data_text.startswith("```json"):
                data_text = data_text[7:]
            if data_text.endswith("```"):
                data_text = data_text[:-3]

            parsed = json.loads(data_text.strip())
            act = parsed.get("action")
            param = parsed.get("param", "")
            resp = parsed.get("response", "")

            if act == "GET_TIME":
                return f"Sir, the time is {PCController.get_time()}"
            elif act == "GET_IP":
                return f"Your IP address is {PCController.get_ip()}"
            elif act == "SEARCH_WIKI":
                return PCController.search_wikipedia(param)
            elif act == "OPEN_GOOGLE":
                PCController.open_google(param)
                return resp or f"Searching Google for {param}"
            elif act == "OPEN_YOUTUBE":
                return PCController.open_youtube(param)
            elif act == "VOLUME_UP":
                return PCController.volume_control("up")
            elif act == "VOLUME_DOWN":
                return PCController.volume_control("down")
            elif act == "MUTE":
                return PCController.volume_control("mute")
            elif act == "BRIGHTNESS_UP":
                return PCController.set_brightness(+15)
            elif act == "BRIGHTNESS_DOWN":
                return PCController.set_brightness(-15)
            elif act == "SCREENSHOT":
                return PCController.take_screenshot()
            elif act == "RECORD_SCREEN":
                return PCController.record_screen()
            elif act == "OPEN_CAM":
                return PCController.open_camera()
            elif act == "OPEN_APP":
                return PCController.open_application(param)
            elif act == "CLOSE_APP":
                return PCController.close_application(param)
            elif act == "CALCULATE":
                return PCController.calculate(param)
            elif act == "JOKE":
                return PCController.get_joke()
            elif act == "SYSTEM_CHECK":
                return PCController.check_system(param)
            elif act == "POWER":
                return PCController.system_power(param)
            elif act == "EMPTY_RECYCLE_BIN":
                return PCController.empty_recycle_bin()
            elif act == "CREATE_FOLDER":
                return PCController.create_desktop_folder(param)
            elif act == "GENERAL_TALK":
                return resp or "I am here to assist you."

        except Exception as e:
            print(f"LLM parsing failed: {e}")

        return None
