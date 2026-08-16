import pyttsx3
import random
import speech_recognition as sr
import datetime
import time
import wikipedia
import webbrowser
import sys
import operator
import pywhatkit as wk
import os
import requests
import cv2
import numpy as np
import wmi
from PIL import Image
import pyautogui
import psutil



engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 150)
def speak(audio):
    engine.say(audio)
    engine.runAndWait()
def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour>=0 and hour<12:
        speak("Good Morning!")
    elif hour>=12 and hour<18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    speak("Ready To Comply. What can I do for you?")


def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        try:
            audio = r.listen(source)
            print("Recognizing...")
            query = r.recognize_google(audio, language='en-in')
            print(f"User said: {query}\n")
        except Exception as e:
            print("Say that again please...")
            return "None" 
    return query  

def run_cli():
    wishMe()
    while True:
        query = takeCommand()
        if query is None:  
            continue
        query = query.lower()
        if "unknown" in query:
            print("yes sir")
            speak("yes sir")

        elif "who are you" in query:
            print("I am your AI assistant")
            speak("I am your AI assistant")
            print("I can help you with various tasks")
            speak("I can help you with various tasks")

        elif "who created you" in query:
            print("I'm an AI assistant created using Python")
            speak("I'm an AI assistant created using Python")

        elif "what is" in query and "ip" not in query:
            speak("Searching Wikipedia...")
            query = query.replace("what is", "")
            try:
                results = wikipedia.summary(query, sentences=2)

                speak("According to Wikipedia")
                print(results)
                speak(results)
            except wikipedia.exceptions.PageError:
                speak("Sorry, I couldn't find any information on that topic.")
            except Exception as e:
                speak("An error occurred while searching Wikipedia.")
                print(f"Error: {e}")
        
        elif "who is" in query and "ip" not in query:
            speak("Searching Wikipedia...")
            query = query.replace("who is", "")
            try:
                results = wikipedia.summary(query, sentences=2)
                speak("According to Wikipedia")
                print(results)
                speak(results)
            except wikipedia.exceptions.PageError:
                speak("Sorry, I couldn't find any information on that person.")
            except Exception as e:
                speak("An error occurred while searching Wikipedia.")
                print(f"Error: {e}")

        elif "just open google" in query:
            webbrowser.open("google.com")

        elif "open google" in query:
            speak("What do you want to search on Google?")
            search_query = takeCommand() 
            if search_query and search_query.lower() != "none":
                url = f"https://www.google.com/search?q={search_query}"
                webbrowser.open(url)
        elif "just open youtube" in query:
            webbrowser.open("youtube.com")
        elif "open youtube" in query:
            speak("What do you want to watch?")
            youtube_search_query = takeCommand()
            if youtube_search_query and youtube_search_query.lower() != "none":
                try:
                    speak("Opening YouTube video...")
                    wk.playonyt(youtube_search_query)
                except Exception as e:
                    speak("Sorry, I encountered an error while searching YouTube")
                    print(f"Error: {str(e)}")
            else:
                speak("Sorry, I couldn't understand what you want to watch")            
        elif "Search on Youtube" in query:
            query = query.replace("Search on Youtube","")
            webbrowser.open(f"www.youtube.com/search?q={query}")
        elif "close browser" in query:
            os.system("taskkill /f /im chrome.exe")

        elif 'exit' in query: 
            speak("Bye,Have a nice day!")
            break  
        elif 'play music' in query:
            try:
                music_dir = os.path.expanduser('~\\Music')
                if os.path.exists(music_dir):
                    songs = [f for f in os.listdir(music_dir) if f.endswith(('.mp3', '.wav', '.m4a'))]
                    if songs:
                        os.startfile(os.path.join(music_dir, random.choice(songs)))
                    else:
                        speak("No music files found in the Music directory")
                else:
                    speak("Music directory not found")
            except Exception as e:
                speak("Error playing music")
                print(f"Error: {str(e)}")

        elif 'play kabir singh movie' in query:
            try:
                movie_path = "C:\\kabir singh\\rohit.mkv"
                if os.path.exists(movie_path):
                    os.startfile(movie_path)
                else:
                    speak("Movie file not found")
            except Exception as e:
                speak("Error playing movie")
                print(f"Error: {str(e)}")
        elif 'close movie' in query:
            os.system("taskkill /f /im vlc.exe")
        elif 'close music' in query:
            os.system("taskkill /f /im vlc.exe")
        elif 'the time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"Sir, the time is {strTime}")
        elif "shut down the system" in query:
            os.system("shutdown /s /t 5")
        elif "restart the system" in query:
            os.system("shutdown /r /t 5")
        elif "Lock the system" in query:
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        elif "open notepad" in query:
            npath = "C:\\windows\\notepad.exe"
            os.startfile(npath)
        elif "close notepad" in query:
            os.system("taskkill /f /im notepad.exe")
        elif "open command prompt" in query:
            os.system("start cmd")
        elif "close command prompt" in query:
            os.system("taskkill /f /im cmd.exe")
        elif "open camera" in query:
            cap = cv2.VideoCapture(0)
            while True:
                ret, img = cap.read()
                cv2.imshow('webcam', img)
                k = cv2.waitKey(50)
                if k==27:
                    break
            cap.release()
            cv2.destroyAllWindows()
        elif "hello" in query or "hi" in query or "how are you" in query:
            greetings = ["Hello! How can I assist you today?", "Hi there! What can I do for you?", "Greetings! Ready to help."]
            response = random.choice(greetings)
            print("Assistant says: " + response)
            speak(response)


        elif "go to sleep" in query:
           speak(' alright then, I am switching off')
           sys.exit()
        elif "calculate" in query:
            r = sr.Recognizer()
            with sr.Microphone() as source:
                speak("Ready for calculation")
                print("Listening for equation...")
                r.pause_threshold = 1
                r.energy_threshold = 300
                r.dynamic_energy_threshold = True
                try:
                    audio = r.listen(source, timeout=10, phrase_time_limit=7)
                    print("Recognizing...")
                    my_string = r.recognize_google(audio).lower()
                    print(f"Recognized equation: {my_string}")

                    def get_operator_fn(op):
                        operators = {
                            '+': operator.add,
                            '-': operator.sub,
                            'x': operator.mul,
                            '*': operator.mul,
                            '/': operator.__truediv__,
                            'divided': operator.__truediv__,
                            'divided by': operator.__truediv__,
                            'plus': operator.add,
                            'minus': operator.sub,
                            'times': operator.mul,
                            'multiply': operator.mul,
                            'multiplied by': operator.mul,
                            'divide': operator.__truediv__,
                            'divide by': operator.__truediv__
                        }
                        return operators.get(op.lower().strip())

                    def clean_number(num_str):
                        # Handle word numbers
                        word_to_num = {
                            'one': '1', 'two': '2', 'three': '3', 'four': '4',
                            'five': '5', 'six': '6', 'seven': '7', 'eight': '8',
                            'nine': '9', 'zero': '0', 'ten': '10'
                        }
                        for word, num in word_to_num.items():
                            num_str = num_str.replace(word, num)
                        
                        # Remove any non-numeric characters except decimal point and negative sign
                        cleaned = ''.join(c for c in num_str if c.isdigit() or c in '.-')
                        try:
                            return float(cleaned)
                        except ValueError:
                            raise ValueError(f"Invalid number: {num_str}")

                    def eval_binary_expr(op1, oper, op2):
                        try:
                            operator_fn = get_operator_fn(oper)
                            if operator_fn is None:
                                raise ValueError(f"Invalid operator: {oper}")
                            num1 = clean_number(op1)
                            num2 = clean_number(op2)
                            if operator_fn == operator.__truediv__ and num2 == 0:
                                speak("Cannot divide by zero")
                                return "undefined"
                            result = operator_fn(num1, num2)
                            # Format result to avoid unnecessary decimal places
                            return int(result) if result.is_integer() else result
                        except Exception as e:
                            raise ValueError(f"Calculation error: {str(e)}")

                    # Validate and process the equation
                    try:
                        # Clean up the input string
                        equation = my_string.strip().lower()
                        
                        # List of valid operators for validation
                        valid_operators = ['+', '-', 'x', '*', '/', 'divided by', 'times', 'plus', 'minus', 
                                         'multiply', 'multiplied by', 'divide', 'divide by', 'divided']
                        
                        # Check if any valid operator is present
                        if not any(op in equation for op in valid_operators):
                            speak("Please say a valid equation like 5 plus 3")
                            continue

                        # Replace word operators with symbols and standardize spacing
                        operator_replacements = {
                            'divided by': ' / ',
                            'divided': ' / ',
                            'divide by': ' / ',
                            'divide': ' / ',
                            'times': ' * ',
                            'multiplied by': ' * ',
                            'multiply': ' * ',
                            'plus': ' + ',
                            'minus': ' - '
                        }
                        for word_op, symbol in operator_replacements.items():
                            equation = equation.replace(word_op, symbol)

                        # Split the equation and clean up parts
                        parts = [p.strip() for p in equation.split() if p.strip()]
                        parts = [p for p in parts if p in ['+', '-', '*', '/', 'x'] or any(c.isdigit() or c.isalpha() for c in p)]
                        
                        # Handle special cases and validate
                        if len(parts) < 3:
                            raise ValueError("Incomplete equation")
                        elif len(parts) > 3:
                            # Find the operator and split around it
                            for i, part in enumerate(parts):
                                if part in ['+', '-', '*', '/', 'x']:
                                    num1 = ' '.join(parts[:i])
                                    operator = part
                                    num2 = ' '.join(parts[i+1:])
                                    parts = [num1, operator, num2]
                                    break
                            if len(parts) != 3:
                                raise ValueError("Could not parse equation")

                        # Perform calculation
                        result = eval_binary_expr(parts[0], parts[1], parts[2])
                        speak(f"Result is {result}")
                        print(f"Calculation: {parts[0]} {parts[1]} {parts[2]} = {result}")
                        
                    except ValueError as e:
                        speak(str(e))
                        print(f"Error: {e}")
                    except Exception as e:
                        speak("Could not calculate that equation")
                        print(f"Calculation error: {e}")
                        
                except sr.UnknownValueError:
                    speak("Sorry, I couldn't understand what you said")
                except sr.RequestError:
                    speak("Sorry, there was an error with the speech recognition service")
                except Exception as e:
                    speak("An unexpected error occurred")
                    print(f"Error: {e}")

        elif "ip address" in query:
            speak("Checking...")
            try:
                ipAdd = requests.get('https://api.ipify.org').text
                print(f"Your IP Address: {ipAdd}")
                speak("Your IP address is")
                speak(ipAdd)
            except Exception as e:
                speak("Failed to retrieve IP address. Please check your network connection.")
                print(f"Error: {e}")
                
        elif "send whatsapp message" in query:
            try:
                speak("To whom should I send the message? Please say the phone number.")
                phone_number = takeCommand()
                if phone_number and phone_number.lower() != "none":
                    # Remove any spaces or special characters from phone number
                    phone_number = ''.join(filter(str.isdigit, phone_number))
                    speak("What message should I send?")
                    message = takeCommand()
                    if message and message.lower() != "none":
                        speak("Sending WhatsApp message...")
                        # Get current time for scheduling message
                        now = datetime.datetime.now()
                        # Schedule message 2 minutes from now to allow WhatsApp Web to load
                        wk.sendwhatmsg(f"+{phone_number}", message, now.hour, now.minute + 2)
                        speak("Message has been sent successfully!")
                    else:
                        speak("Sorry, I couldn't understand the message")
                else:
                    speak("Sorry, I couldn't understand the phone number")
            except Exception as e:
                speak("Sorry, I encountered an error while sending the WhatsApp message")
                print(f"Error: {str(e)}")

        elif "whatsapp call" in query:
            try:
                speak("Please say the phone number you want to call")
                phone_number = takeCommand()
                if phone_number and phone_number.lower() != "none":
                    phone_number = ''.join(filter(str.isdigit, phone_number))
                    speak("Initiating WhatsApp call...")
                    wk.callwhatsapp(f"+{phone_number}")
                    speak("WhatsApp call initiated!")
                else:
                    speak("Sorry, I couldn't understand the phone number")
            except Exception as e:
                speak("Sorry, I encountered an error while making the WhatsApp call")
                print(f"Error: {str(e)}")

        elif "open whatsapp chat" in query:
            try:
                speak("Please say the phone number")
                phone_number = takeCommand()
                if phone_number and phone_number.lower() != "none":
                    phone_number = ''.join(filter(str.isdigit, phone_number))
                    speak("Opening WhatsApp chat...")
                    wk.open_web()
                    time.sleep(2)  # Wait for WhatsApp Web to load
                    wk.sendwhatmsg_instantly(f"+{phone_number}", "Hi", wait_time=15, tab_close=True)
                    speak("WhatsApp chat opened!")
                else:
                    speak("Sorry, I couldn't understand the phone number")
            except Exception as e:
                speak("Sorry, I encountered an error while opening WhatsApp chat")
                print(f"Error: {str(e)}")

        elif "volume up" in query:
            for _ in range(15):
                pyautogui.press("volumeup")

        elif "volume down" in query:
            for _ in range(16):
                pyautogui.press("volumedown")

        elif "mute" in query:
            pyautogui.press("volumemute")

        elif "refresh" in query:
            pyautogui.moveTo(1551,551, 2)
            pyautogui.click(x=1551, y=551, clicks=1, interval=0, button='right')
            pyautogui.moveTo(1620,667, 1)
            pyautogui.click(x=1620, y=667, clicks=1, interval=0, button='left')

        elif "scroll down" in query:
            pyautogui.scroll(1000)

        elif "drag visual studio to the right" in query:
            pyautogui.moveTo(46, 31, 2)
            pyautogui.dragRel(1857, 31, 2)

        elif "rectangular spiral" in query:
            pyautogui.hotkey('win')
            time.sleep(1)
            pyautogui.write('paint')
            time.sleep(1)
            pyautogui.press('enter')
            pyautogui.moveTo(100, 193, 1)
            pyautogui.rightClick()
            pyautogui.click()
            distance = 300
            while distance > 0:
                pyautogui.dragRel(distance, 0, 0.1, button="left")
                distance = distance - 10
                pyautogui.dragRel(0, distance, 0.1, button="left")
                pyautogui.dragRel(-distance, 0, 0.1, button="left")
                distance = distance - 10
                pyautogui.dragRel(0, -distance, 0.1, button="left")

        elif "close paint" in query:
            os.system("taskkill /f /im mspaint.exe")

        # Screen Control
        elif "take screenshot" in query:
            speak("Taking screenshot")
            screenshot = pyautogui.screenshot()
            screenshot_path = os.path.join(os.path.expanduser("~"), "Desktop", f"screenshot_{int(time.time())}.png")
            screenshot.save(screenshot_path)
            speak("Screenshot saved to desktop")

        elif "start screen recording" in query:
            speak("Starting screen recording for 10 seconds")
            screen_size = pyautogui.size()
            output_path = os.path.join(os.path.expanduser("~"), "Desktop", f"screen_recording_{int(time.time())}.avi")
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(output_path, fourcc, 20.0, (screen_size.width, screen_size.height))
            start_rec = time.time()
            while time.time() - start_rec < 10:
                screenshot = pyautogui.screenshot()
                frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                out.write(frame)
                time.sleep(0.04)
            out.release()
            speak("Screen recording saved to desktop")


        elif "increase brightness" in query:
            try:
                w = wmi.WMI(namespace='root/WMI')
                brightness_methods = w.WmiMonitorBrightnessMethods()
                if brightness_methods:
                    current = w.WmiMonitorBrightness()[0].CurrentBrightness
                    new_brightness = min(current + 10, 100)
                    brightness_methods[0].WmiSetBrightness(new_brightness, 0)
                    speak(f"Brightness increased to {new_brightness} percent")
                else:
                    speak("Brightness control not supported on this device")
            except Exception as e:
                speak("Error adjusting brightness")
                print(f"Error: {str(e)}")

        elif "decrease brightness" in query:
            try:
                w = wmi.WMI(namespace='root/WMI')
                brightness_methods = w.WmiMonitorBrightnessMethods()
                if brightness_methods:
                    current = w.WmiMonitorBrightness()[0].CurrentBrightness
                    new_brightness = max(current - 10, 0)
                    brightness_methods[0].WmiSetBrightness(new_brightness, 0)
                    speak(f"Brightness decreased to {new_brightness} percent")
                else:
                    speak("Brightness control not supported on this device")
            except Exception as e:
                speak("Error adjusting brightness")
                print(f"Error: {str(e)}")


        # File Management
        elif "create folder" in query:
            speak("What should I name the folder?")
            folder_name = takeCommand()
            if folder_name and folder_name.lower() != "none":
                folder_path = os.path.join(os.path.expanduser("~"), "Desktop", folder_name)
                try:
                    os.makedirs(folder_path)
                    speak(f"Created folder {folder_name} on desktop")
                except Exception as e:
                    speak(f"Error creating folder: {str(e)}")

        elif "delete folder" in query:
            speak("Which folder should I delete?")
            folder_name = takeCommand()
            if folder_name and folder_name.lower() != "none":
                folder_path = os.path.join(os.path.expanduser("~"), "Desktop", folder_name)
                try:
                    os.rmdir(folder_path)
                    speak(f"Deleted folder {folder_name} from desktop")
                except Exception as e:
                    speak(f"Error deleting folder: {str(e)}")

        # Entertainment
        elif "tell me a joke" in query:
            jokes = [
                "Why don't programmers like nature? It has too many bugs!",
                "Why did the computer go to the doctor? Because it had a virus!",
                "What do you call a computer that sings? A Dell!",
                "Why did the programmer quit his job? Because he didn't get arrays!",
                "What's a computer's favorite snack? Microchips!"
            ]
            joke = random.choice(jokes)
            print(joke)
            speak(joke)

        elif "riddle me" in query:
            riddles = [
                {"question": "What has keys, but no locks; space, but no room; and you can enter, but not go in?", "answer": "A keyboard"},
                {"question": "What gets wetter and wetter the more it dries?", "answer": "A towel"},
                {"question": "What has a head and a tail that will never meet?", "answer": "A coin"},
                {"question": "What has cities, but no houses; forests, but no trees; and rivers, but no water?", "answer": "A map"}
            ]
            riddle = random.choice(riddles)
            print("Here's your riddle:")
            speak("Here's your riddle:")
            print(riddle["question"])
            speak(riddle["question"])
            time.sleep(1)
            speak("Would you like to hear the answer?")
            response = takeCommand()
            if response and "yes" in response.lower():
                print("The answer is: " + riddle["answer"])
                speak("The answer is: " + riddle["answer"])

        # Microsoft Office Applications
        elif "open word" in query:
            os.startfile("C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE")
        elif "close word" in query:
            os.system("taskkill /f /im WINWORD.EXE")
        elif "open excel" in query:
            os.startfile("C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE")
        elif "close excel" in query:
            os.system("taskkill /f /im EXCEL.EXE")
        elif "open powerpoint" in query:
            os.startfile("C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE")
        elif "close powerpoint" in query:
            os.system("taskkill /f /im POWERPNT.EXE")

        # Media Players
        elif "open vlc" in query:
            os.startfile("C:\\Program Files\\VideoLAN\\VLC\\vlc.exe")
        elif "close vlc" in query:
            os.system("taskkill /f /im vlc.exe")
        elif "open windows media player" in query:
            os.startfile("C:\\Program Files (x86)\\Windows Media Player\\wmplayer.exe")
        elif "close windows media player" in query:
            os.system("taskkill /f /im wmplayer.exe")

        # Browsers
        elif "open firefox" in query:
            firefox_paths = [
                "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
                "C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe",
                os.path.expandvars("%LOCALAPPDATA%\\Mozilla Firefox\\firefox.exe")
            ]
            firefox_found = False
            for path in firefox_paths:
                if os.path.exists(path):
                    os.startfile(path)
                    firefox_found = True
                    break
            if not firefox_found:
                speak("Firefox is not installed or could not be found in common locations")
                print("Firefox not found in common installation paths")
        elif "close firefox" in query:
            os.system("taskkill /f /im firefox.exe")
        elif "open edge" in query:
            edge_paths = [
                "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
                "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe"
            ]
            edge_found = False
            for path in edge_paths:
                if os.path.exists(path):
                    os.startfile(path)
                    edge_found = True
                    break
            if not edge_found:
                speak("Microsoft Edge is not installed or could not be found in common locations")
                print("Microsoft Edge not found in common installation paths")
        elif "close edge" in query:
            os.system("taskkill /f /im msedge.exe")

        # System Utilities
        elif "open task manager" in query:
            os.startfile("taskmgr")
        elif "open control panel" in query:
            os.startfile("control")
        elif "open calculator" in query:
            os.startfile("calc")
        elif "close calculator" in query:
            os.system("taskkill /f /im calculator.exe")
        elif "open file explorer" in query:
            os.startfile("explorer")

        # Development Tools
        elif "open visual studio code" in query:
            vscode_path = os.path.expandvars("%LOCALAPPDATA%\\Programs\\Microsoft VS Code\\Code.exe")
            if os.path.exists(vscode_path):
                os.startfile(vscode_path)
            else:
                speak("Visual Studio Code is not installed or could not be found")
                print("VS Code not found in common installation path")
        elif "close visual studio code" in query:
            os.system("taskkill /f /im Code.exe")
        elif "open visual studio" in query:
            vs_paths = [
                "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\Common7\\IDE\\devenv.exe",
                "C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\Community\\Common7\\IDE\\devenv.exe"
            ]
            vs_found = False
            for path in vs_paths:
                if os.path.exists(path):
                    os.startfile(path)
                    vs_found = True
                    break
            if not vs_found:
                speak("Visual Studio is not installed or could not be found in common locations")
                print("Visual Studio not found in common installation paths")
        elif "close visual studio" in query:
            os.system("taskkill /f /im devenv.exe")

        # Communication Apps
        elif "open teams" in query:
            try:
                teams_path = os.path.expandvars("%LOCALAPPDATA%\\Microsoft\\Teams\\current\\Teams.exe")
                if os.path.exists(teams_path):
                    os.startfile(teams_path)
                else:
                    speak("Microsoft Teams is not installed or could not be found")
            except Exception as e:
                speak("Error opening Microsoft Teams")
                print(f"Error: {str(e)}")

        elif "close teams" in query:
            os.system("taskkill /f /im Teams.exe")
        elif "open skype" in query:
            os.startfile("C:\\Program Files\\Microsoft Office\\root\\Office16\\lync.exe")
        elif "close skype" in query:
            os.system("taskkill /f /im lync.exe")

        # Graphics and Design
        elif "open photoshop" in query:
            os.startfile("C:\\Program Files\\Adobe\\Adobe Photoshop 2023\\Photoshop.exe")
        elif "close photoshop" in query:
            os.system("taskkill /f /im Photoshop.exe")
        elif "open illustrator" in query:
            os.startfile("C:\\Program Files\\Adobe\\Adobe Illustrator 2023\\Support Files\\Contents\\Windows\\Illustrator.exe")
        elif "close illustrator" in query:
            os.system("taskkill /f /im Illustrator.exe")

        # Web Interactions and Search Engines
        elif "search on bing" in query:
            speak("What would you like to search on Bing?")
            search_query = takeCommand()
            if search_query and search_query.lower() != "none":
                url = f"https://www.bing.com/search?q={search_query}"
                webbrowser.open(url)

        elif "search on duckduckgo" in query:
            speak("What would you like to search on DuckDuckGo?")
            search_query = takeCommand()
            if search_query and search_query.lower() != "none":
                url = f"https://duckduckgo.com/?q={search_query}"
                webbrowser.open(url)

        elif "open github" in query:
            webbrowser.open("https://github.com")

        elif "open linkedin" in query:
            webbrowser.open("https://linkedin.com")

        elif "open twitter" in query:
            webbrowser.open("https://twitter.com")

        elif "open instagram" in query:
            webbrowser.open("https://instagram.com")

        elif "open reddit" in query:
            webbrowser.open("https://reddit.com")

        elif "translate" in query:
            speak("What would you like me to translate?")
            text = takeCommand()
            if text and text.lower() != "none":
                speak("Which language should I translate to?")
                lang = takeCommand()
                if lang and lang.lower() != "none":
                    url = f"https://translate.google.com/?text={text}&tl={lang}"
                    webbrowser.open(url)
                    speak("Opening Google Translate")

        elif "weather" in query:
            speak("Which city's weather would you like to know?")
            city = takeCommand()
            if city and city.lower() != "none":
                url = f"https://www.google.com/search?q=weather+in+{city}"
                webbrowser.open(url)
                speak(f"Showing weather for {city}")

        # System Monitoring and Power Management
        elif "check cpu usage" in query:
            cpu_percent = psutil.cpu_percent(interval=1)
            speak(f"CPU usage is {cpu_percent} percent")

        elif "check memory usage" in query:
            memory = psutil.virtual_memory()
            speak(f"Memory usage is {memory.percent} percent")

        elif "check battery" in query:
            battery = psutil.sensors_battery()
            if battery:
                speak(f"Battery percentage is {battery.percent} percent")
                if battery.power_plugged:
                    speak("The system is plugged in")
                else:
                    speak("The system is running on battery")
            else:
                speak("No battery found")

        elif "hibernate system" in query:
            speak("Putting system into hibernate mode")
            os.system("shutdown /h")

        elif "sleep mode" in query:
            speak("Putting system into sleep mode")
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

        elif "empty recycle bin" in query:
            try:
                import ctypes
                ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)
                speak("Recycle bin emptied successfully")
            except Exception as e:
                speak("Error emptying recycle bin")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        run_cli()
    else:
        from app_gui import launch_gui
        launch_gui()