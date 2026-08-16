import os
import sys
import time
import random
import datetime
import operator
import webbrowser
import requests
import cv2
import numpy as np

# Optional / OS-dependent libraries with safe import fallbacks
try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    import psutil
except ImportError:
    psutil = None

try:
    import wmi
except ImportError:
    wmi = None

try:
    import winshell
except ImportError:
    winshell = None

try:
    import pywhatkit as wk
except ImportError:
    wk = None

try:
    import wikipedia
except ImportError:
    wikipedia = None


class PCController:
    """Handles all PC automation, app launching, system settings, media, and utilities."""

    @staticmethod
    def get_time() -> str:
        return datetime.datetime.now().strftime("%H:%M:%S")

    @staticmethod
    def get_ip() -> str:
        try:
            return requests.get("https://api.ipify.org", timeout=5).text
        except Exception as e:
            return f"Error: {e}"

    @staticmethod
    def search_wikipedia(query: str) -> str:
        if not wikipedia:
            return "Wikipedia package is not installed."
        clean_query = query.replace("what is", "").replace("who is", "").strip()
        try:
            return wikipedia.summary(clean_query, sentences=2)
        except wikipedia.exceptions.PageError:
            return f"No Wikipedia results found for '{clean_query}'."
        except Exception as e:
            return f"Wikipedia error: {e}"

    @staticmethod
    def open_google(query: str = ""):
        if query and query.lower() != "none":
            url = f"https://www.google.com/search?q={query}"
            webbrowser.open(url)
        else:
            webbrowser.open("https://google.com")

    @staticmethod
    def open_youtube(query: str = ""):
        if query and query.lower() != "none":
            if wk:
                try:
                    wk.playonyt(query)
                    return f"Playing '{query}' on YouTube"
                except Exception:
                    pass
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
            return f"Searching YouTube for '{query}'"
        else:
            webbrowser.open("https://youtube.com")
            return "Opening YouTube"

    @staticmethod
    def volume_control(action: str):
        if not pyautogui:
            return "pyautogui not installed."
        if action == "up":
            for _ in range(10):
                pyautogui.press("volumeup")
            return "Volume increased"
        elif action == "down":
            for _ in range(10):
                pyautogui.press("volumedown")
            return "Volume decreased"
        elif action == "mute":
            pyautogui.press("volumemute")
            return "Volume muted"

    @staticmethod
    def set_brightness(change: int) -> str:
        """Adjusts monitor brightness by +change or -change."""
        if not wmi:
            return "WMI module not available."
        try:
            w = wmi.WMI(namespace='root/WMI')
            brightness_methods = w.WmiMonitorBrightnessMethods()
            if brightness_methods:
                current = w.WmiMonitorBrightness()[0].CurrentBrightness
                new_brightness = max(0, min(100, current + change))
                brightness_methods[0].WmiSetBrightness(new_brightness, 0)
                return f"Brightness adjusted to {new_brightness}%"
            return "Brightness control not supported on this monitor/device."
        except Exception as e:
            return f"Brightness adjustment failed: {e}"

    @staticmethod
    def take_screenshot() -> str:
        if not pyautogui:
            return "pyautogui not available."
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        filename = f"screenshot_{int(time.time())}.png"
        filepath = os.path.join(desktop_path, filename)
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)
        return f"Screenshot saved to desktop as {filename}"

    @staticmethod
    def record_screen(stop_checker=None) -> str:
        if not pyautogui:
            return "pyautogui not available."
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        output_path = os.path.join(desktop_path, f"screen_recording_{int(time.time())}.avi")
        screen_size = pyautogui.size()
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(output_path, fourcc, 20.0, (screen_size.width, screen_size.height))
        
        start_time = time.time()
        # Record up to 30 seconds or until stop_checker returns True
        while time.time() - start_time < 30:
            if stop_checker and stop_checker():
                break
            screenshot = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            out.write(frame)
            time.sleep(0.04)
        out.release()
        return f"Screen recording saved to desktop"

    @staticmethod
    def open_camera():
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return "Camera could not be opened."
        while True:
            ret, img = cap.read()
            if not ret:
                break
            cv2.imshow('Webcam Feed (Press ESC to close)', img)
            k = cv2.waitKey(30)
            if k == 27:
                break
        cap.release()
        cv2.destroyAllWindows()
        return "Camera closed"

    @staticmethod
    def open_application(app_name: str) -> str:
        app_map = {
            "notepad": "notepad.exe",
            "command prompt": "start cmd",
            "cmd": "start cmd",
            "calculator": "calc",
            "file explorer": "explorer",
            "explorer": "explorer",
            "task manager": "taskmgr",
            "control panel": "control",
            "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
            "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
            "powerpoint": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
            "vlc": r"C:\Program Files\VideoLAN\VLC\vlc.exe",
        }

        app_key = app_name.lower().strip()
        if app_key in app_map:
            os.system(app_map[app_key]) if app_map[app_key].startswith("start ") else os.startfile(app_map[app_key]) if os.path.isabs(app_map[app_key]) or "." in app_map[app_key] else os.system(app_map[app_key])
            return f"Opened {app_name}"

        # Visual Studio Code
        if "code" in app_key or "vs code" in app_key or "visual studio code" in app_key:
            vscode_path = os.path.expandvars("%LOCALAPPDATA%\\Programs\\Microsoft VS Code\\Code.exe")
            if os.path.exists(vscode_path):
                os.startfile(vscode_path)
                return "Opened Visual Studio Code"
            os.system("code")
            return "Attempting to launch VS Code"

        # Edge / Firefox
        if "edge" in app_key:
            os.system("start msedge")
            return "Opened Microsoft Edge"
        if "firefox" in app_key:
            os.system("start firefox")
            return "Opened Firefox"
        if "chrome" in app_key:
            os.system("start chrome")
            return "Opened Chrome"

        # Fallback to system start command
        try:
            os.system(f"start {app_name}")
            return f"Attempting to open {app_name}"
        except Exception as e:
            return f"Failed to open {app_name}: {e}"

    @staticmethod
    def close_application(app_name: str) -> str:
        kill_map = {
            "notepad": "notepad.exe",
            "command prompt": "cmd.exe",
            "cmd": "cmd.exe",
            "calculator": "calculator.exe",
            "word": "WINWORD.EXE",
            "excel": "EXCEL.EXE",
            "powerpoint": "POWERPNT.EXE",
            "vlc": "vlc.exe",
            "chrome": "chrome.exe",
            "firefox": "firefox.exe",
            "edge": "msedge.exe",
            "vs code": "Code.exe",
            "code": "Code.exe",
            "visual studio": "devenv.exe",
            "paint": "mspaint.exe",
            "teams": "Teams.exe"
        }
        app_key = app_name.lower().strip()
        exe_name = kill_map.get(app_key, f"{app_key}.exe")
        os.system(f"taskkill /f /im {exe_name}")
        return f"Closed {app_name}"

    @staticmethod
    def calculate(expression: str) -> str:
        """Parses and computes simple math expressions."""
        try:
            # Basic cleanup for natural spoken math
            expr = expression.replace("plus", "+").replace("minus", "-").replace("times", "*").replace("multiplied by", "*").replace("divided by", "/").replace("x", "*")
            allowed_chars = "0123456789+-*/.() "
            cleaned = "".join(c for c in expr if c in allowed_chars)
            if not cleaned.strip():
                return "Could not extract numbers from calculation."
            res = eval(cleaned)
            return f"Result is {res}"
        except Exception as e:
            return f"Calculation error: {e}"

    @staticmethod
    def send_whatsapp(phone: str, message: str) -> str:
        if not wk:
            return "pywhatkit library not available."
        clean_phone = ''.join(filter(str.isdigit, phone))
        now = datetime.datetime.now()
        try:
            wk.sendwhatmsg(f"+{clean_phone}", message, now.hour, now.minute + 2)
            return "WhatsApp message scheduled."
        except Exception as e:
            return f"WhatsApp error: {e}"

    @staticmethod
    def check_system(info_type: str) -> str:
        if not psutil:
            return "psutil library not available."
        if info_type == "cpu":
            usage = psutil.cpu_percent(interval=1)
            return f"CPU usage is {usage}%"
        elif info_type == "memory":
            mem = psutil.virtual_memory()
            return f"Memory usage is {mem.percent}%"
        elif info_type == "battery":
            bat = psutil.sensors_battery()
            if bat:
                status = "plugged in" if bat.power_plugged else "on battery"
                return f"Battery is at {bat.percent}% ({status})"
            return "No battery detected."
        return "Unknown system check request."

    @staticmethod
    def create_desktop_folder(folder_name: str) -> str:
        if not folder_name or folder_name.lower() == "none":
            return "Invalid folder name."
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        target = os.path.join(desktop, folder_name)
        try:
            os.makedirs(target, exist_ok=True)
            return f"Created folder '{folder_name}' on Desktop"
        except Exception as e:
            return f"Error creating folder: {e}"

    @staticmethod
    def delete_desktop_folder(folder_name: str) -> str:
        if not folder_name or folder_name.lower() == "none":
            return "Invalid folder name."
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        target = os.path.join(desktop, folder_name)
        try:
            os.rmdir(target)
            return f"Deleted folder '{folder_name}' from Desktop"
        except Exception as e:
            return f"Error deleting folder: {e}"

    @staticmethod
    def get_joke() -> str:
        jokes = [
            "Why don't programmers like nature? It has too many bugs!",
            "Why did the computer go to the doctor? Because it had a virus!",
            "What do you call a computer that sings? A Dell!",
            "Why did the programmer quit his job? Because he didn't get arrays!",
            "What's a computer's favorite snack? Microchips!"
        ]
        return random.choice(jokes)

    @staticmethod
    def system_power(action: str) -> str:
        if action == "shutdown":
            os.system("shutdown /s /t 5")
            return "System shutting down in 5 seconds."
        elif action == "restart":
            os.system("shutdown /r /t 5")
            return "System restarting in 5 seconds."
        elif action == "lock":
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return "Locking system workstation."
        elif action == "sleep":
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return "Putting system to sleep."
        elif action == "hibernate":
            os.system("shutdown /h")
            return "Hibernating system."
        return "Unknown power action."

    @staticmethod
    def refresh_desktop() -> str:
        if pyautogui:
            pyautogui.press("f5")
            return "Refreshed desktop."
        return "pyautogui not available."

    @staticmethod
    def draw_spiral() -> str:
        if not pyautogui:
            return "pyautogui not available."
        try:
            os.system("start mspaint")
            time.sleep(1.5)
            sw, sh = pyautogui.size()
            cx, cy = sw // 2, sh // 2
            pyautogui.moveTo(cx, cy)
            pyautogui.click()
            distance = 250
            while distance > 0:
                pyautogui.dragRel(distance, 0, 0.05, button="left")
                distance -= 10
                pyautogui.dragRel(0, distance, 0.05, button="left")
                pyautogui.dragRel(-distance, 0, 0.05, button="left")
                distance -= 10
                pyautogui.dragRel(0, -distance, 0.05, button="left")
            return "Spiral drawn in Paint."
        except Exception as e:
            return f"Error drawing spiral: {e}"

    @staticmethod
    def empty_recycle_bin() -> str:
        try:
            import ctypes
            # Flags: SHERB_NOCONFIRMATION (1) | SHERB_NOPROGRESSUI (2) | SHERB_NOSOUND (4)
            ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)
            return "Recycle Bin emptied successfully."
        except Exception as e:
            if winshell:
                try:
                    winshell.recycle_bin().empty(confirm=False, show_progress=False)
                    return "Recycle Bin emptied successfully."
                except Exception as win_err:
                    return f"Error emptying Recycle Bin: {win_err}"
            return f"Error emptying Recycle Bin: {e}"


