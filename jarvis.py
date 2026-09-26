"""
JARVIS - Upgraded Python Voice Assistant

Features:
- Microsoft Zira voice
- Voice recognition
- Time & Date
- Weather for any city
- Google search
- YouTube search
- Website opening
- Basic calculations
- CS questions
- Notes
- Voice exit
- Close current browser tab
- Close current window
"""

import ast
import datetime
import operator
import subprocess
import webbrowser
import time
from pathlib import Path
from urllib.parse import quote_plus

import requests
import speech_recognition as sr
import pyautogui


# =========================================================
# SETTINGS
# =========================================================

NOTES_FILE = Path("jarvis_notes.txt")

recognizer = sr.Recognizer()

recognizer.pause_threshold = 0.8
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True


# =========================================================
# TEXT TO SPEECH - MICROSOFT ZIRA
# =========================================================

def speak(text):

    print("Jarvis:", text)

    try:

        safe_text = text.replace("'", "''")

        command = f"""
Add-Type -AssemblyName System.Speech

$speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer

$speaker.Volume = 100
$speaker.Rate = 0

$voices = $speaker.GetInstalledVoices()

foreach ($v in $voices) {{
    if ($v.VoiceInfo.Name -match "Zira") {{
        $speaker.SelectVoice($v.VoiceInfo.Name)
        break
    }}
}}

$speaker.Speak('{safe_text}')
"""

        subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-Command",
                command
            ],
            check=False
        )

    except Exception as e:

        print("Voice error:", e)


# =========================================================
# SPEECH RECOGNITION
# =========================================================

def take_command():

    try:

        with sr.Microphone() as source:

            print("\nListening...")

            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.5
            )

            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=10
            )

        print("Recognizing...")

        query = recognizer.recognize_google(audio)

        print("You:", query)

        return query.lower().strip()

    except sr.WaitTimeoutError:

        print("No speech detected.")

        return ""

    except sr.UnknownValueError:

        print("Could not understand.")

        return ""

    except sr.RequestError as e:

        print("Speech service error:", e)

        return ""

    except Exception as e:

        print("Microphone error:", e)

        return ""


# =========================================================
# WEATHER
# =========================================================

def get_weather(city="Sasaram"):

    try:

        city = city.strip()

        if not city:
            city = "Sasaram"

        print(f"Getting weather for {city}...")

        url = (
            f"https://wttr.in/"
            f"{quote_plus(city)}"
            f"?format=j1"
        )

        response = requests.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        current = data["current_condition"][0]

        temperature = current["temp_C"]

        feels_like = current["FeelsLikeC"]

        humidity = current["humidity"]

        condition = current["weatherDesc"][0]["value"]

        answer = (
            f"The current weather in {city} is {condition}. "
            f"The temperature is {temperature} degrees Celsius. "
            f"It feels like {feels_like} degrees Celsius. "
            f"Humidity is {humidity} percent."
        )

        speak(answer)

    except Exception as e:

        print("Weather error:", e)

        speak(
            f"Sorry, I could not get the weather "
            f"for {city}."
        )


# =========================================================
# CALCULATOR
# =========================================================

OPERATORS = {

    ast.Add: operator.add,

    ast.Sub: operator.sub,

    ast.Mult: operator.mul,

    ast.Div: operator.truediv,

    ast.Mod: operator.mod,

    ast.Pow: operator.pow,

    ast.USub: operator.neg,

    ast.UAdd: operator.pos,
}


def calculate_expression(expression):

    try:

        expression = expression.replace(
            "x",
            "*"
        )

        expression = expression.replace(
            "×",
            "*"
        )

        tree = ast.parse(
            expression,
            mode="eval"
        )

        def calculate(node):

            if isinstance(
                node,
                ast.Expression
            ):

                return calculate(
                    node.body
                )

            if isinstance(
                node,
                ast.Constant
            ):

                if isinstance(
                    node.value,
                    (int, float)
                ):

                    return node.value

                raise ValueError

            if isinstance(
                node,
                ast.BinOp
            ):

                left = calculate(
                    node.left
                )

                right = calculate(
                    node.right
                )

                operation = OPERATORS.get(
                    type(node.op)
                )

                if operation is None:

                    raise ValueError

                return operation(
                    left,
                    right
                )

            if isinstance(
                node,
                ast.UnaryOp
            ):

                value = calculate(
                    node.operand
                )

                operation = OPERATORS.get(
                    type(node.op)
                )

                if operation is None:

                    raise ValueError

                return operation(
                    value
                )

            raise ValueError

        return calculate(tree)

    except Exception:

        return None


# =========================================================
# NOTES
# =========================================================

def save_note(note):

    try:

        with open(
            NOTES_FILE,
            "a",
            encoding="utf-8"
        ) as file:

            time_now = (
                datetime.datetime.now()
                .strftime("%d-%m-%Y %I:%M %p")
            )

            file.write(
                f"[{time_now}] {note}\n"
            )

        speak(
            "Your note has been saved."
        )

    except Exception as e:

        print(
            "Note error:",
            e
        )

        speak(
            "Sorry, I could not save the note."
        )


def read_notes():

    try:

        if not NOTES_FILE.exists():

            speak(
                "You don't have any saved notes."
            )

            return

        notes = NOTES_FILE.read_text(
            encoding="utf-8"
        ).strip()

        if not notes:

            speak(
                "You don't have any saved notes."
            )

            return

        print(
            "\n----- JARVIS NOTES -----"
        )

        print(notes)

        print(
            "------------------------"
        )

        speak(
            "I found your saved notes. "
            "I have displayed them on the screen."
        )

    except Exception as e:

        print(
            "Read notes error:",
            e
        )

        speak(
            "Sorry, I could not read your notes."
        )


# =========================================================
# GOOGLE SEARCH
# =========================================================

def google_search(query):

    search_query = query.strip()

    if not search_query:

        speak(
            "What should I search for?"
        )

        return

    speak(
        f"Searching Google for {search_query}."
    )

    url = (
        "https://www.google.com/search?q="
        + quote_plus(search_query)
    )

    webbrowser.open(url)


# =========================================================
# YOUTUBE SEARCH
# =========================================================

def youtube_search(query):

    search_query = query.strip()

    if not search_query:

        speak(
            "What should I search on YouTube?"
        )

        return

    speak(
        f"Searching YouTube for {search_query}."
    )

    url = (
        "https://www.youtube.com/results?search_query="
        + quote_plus(search_query)
    )

    webbrowser.open(url)


# =========================================================
# CLOSE COMMANDS
# =========================================================

def close_current_tab():

    try:

        speak(
            "Closing the current tab."
        )

        time.sleep(0.5)

        pyautogui.hotkey(
            "ctrl",
            "w"
        )

    except Exception as e:

        print(
            "Close tab error:",
            e
        )

        speak(
            "Sorry, I could not close the tab."
        )


def close_current_window():

    try:

        speak(
            "Closing the current window."
        )

        time.sleep(0.5)

        pyautogui.hotkey(
            "alt",
            "f4"
        )

    except Exception as e:

        print(
            "Close window error:",
            e
        )

        speak(
            "Sorry, I could not close the window."
        )


# =========================================================
# BASIC QUESTIONS
# =========================================================

def ask_question(query):

    query = query.lower().strip()

    if "java" in query:

        answer = (
            "Java is a high level, object oriented "
            "programming language. It is widely used "
            "for Android applications, backend "
            "development and enterprise software."
        )

    elif "python" in query:

        answer = (
            "Python is a high level programming "
            "language with simple syntax. It is widely "
            "used in artificial intelligence, machine "
            "learning, web development and automation."
        )

    elif (
        "dsa" in query
        or "data structure" in query
        or "data structures" in query
    ):

        answer = (
            "DSA stands for Data Structures and "
            "Algorithms. It helps programmers store, "
            "organize and process data efficiently."
        )

    elif (
        "artificial intelligence" in query
        or "what is ai" in query
        or query == "ai"
    ):

        answer = (
            "Artificial Intelligence is the ability "
            "of computers to perform tasks that normally "
            "require human intelligence, such as "
            "learning, reasoning and understanding language."
        )

    elif (
        "machine learning" in query
        or query == "ml"
    ):

        answer = (
            "Machine Learning is a branch of artificial "
            "intelligence where computers learn patterns "
            "from data and use those patterns to make "
            "predictions or decisions."
        )

    elif (
        "c++" in query
        or "cpp" in query
        or "c plus plus" in query
    ):

        answer = (
            "C plus plus is a general purpose programming "
            "language. It is commonly used for system "
            "software, games, competitive programming "
            "and high performance applications."
        )

    elif "computer science" in query:

        answer = (
            "Computer Science is the study of computers, "
            "programming, algorithms, data structures, "
            "software, networks and artificial intelligence."
        )

    elif "api" in query:

        answer = (
            "API stands for Application Programming "
            "Interface. It allows different software "
            "applications to communicate with each other."
        )

    elif "github" in query:

        answer = (
            "GitHub is a platform used to store, manage "
            "and collaborate on software projects using Git."
        )

    else:

        answer = (
            "Sorry, I don't know the answer "
            "to that question yet."
        )

    speak(answer)


# =========================================================
# COMMAND HANDLER
# =========================================================

def handle_command(query):

    query = query.lower().strip()

    if not query:

        return True


    # =====================================================
    # EXIT JARVIS
    # =====================================================

    if (
        query in [
            "quit",
            "exit",
            "stop",
            "goodbye",
            "bye"
        ]

        or "stop jarvis" in query

        or "exit jarvis" in query

        or "close jarvis" in query
    ):

        speak(
            "Goodbye. Have a nice day!"
        )

        return False


    # =====================================================
    # CLOSE CURRENT TAB
    # =====================================================

    if (
        query in [
            "close tab",
            "close current tab",
            "close this tab"
        ]

        or "close youtube" in query

        or "close the tab" in query

        or "close current tab" in query
    ):

        close_current_tab()

        return True


    # =====================================================
    # CLOSE CURRENT WINDOW
    # =====================================================

    if (
        query in [
            "close window",
            "close current window",
            "close this window"
        ]

        or "close the window" in query
    ):

        close_current_window()

        return True


    # =====================================================
    # TIME
    # =====================================================

    if (
        "what is the time" in query

        or "current time" in query

        or "tell me the time" in query

        or query == "time"
    ):

        current_time = (
            datetime.datetime.now()
            .strftime("%I:%M %p")
        )

        speak(
            f"The current time is {current_time}."
        )

        return True


    # =====================================================
    # DATE
    # =====================================================

    if (
        "what is the date" in query

        or "today's date" in query

        or "today date" in query

        or query == "date"
    ):

        today = (
            datetime.datetime.now()
            .strftime("%d %B %Y")
        )

        speak(
            f"Today's date is {today}."
        )

        return True


    # =====================================================
    # WEATHER
    # =====================================================

    if (
        "weather" in query

        or "temperature" in query
    ):

        city = "Sasaram"

        words = query.split()

        if "in" in words:

            index = words.index("in")

            if index + 1 < len(words):

                city = " ".join(
                    words[index + 1:]
                )

        elif "of" in words:

            index = words.index("of")

            if index + 1 < len(words):

                city = " ".join(
                    words[index + 1:]
                )

        get_weather(city)

        return True


    # =====================================================
    # GOOGLE SEARCH
    # =====================================================

    if query.startswith(
        "search google for"
    ):

        search_query = query.replace(
            "search google for",
            "",
            1
        ).strip()

        google_search(
            search_query
        )

        return True


    if query.startswith(
        "google search"
    ):

        search_query = query.replace(
            "google search",
            "",
            1
        ).strip()

        google_search(
            search_query
        )

        return True


    # =====================================================
    # YOUTUBE SEARCH
    # =====================================================

    if query.startswith(
        "search youtube for"
    ):

        search_query = query.replace(
            "search youtube for",
            "",
            1
        ).strip()

        youtube_search(
            search_query
        )

        return True


    if query.startswith(
        "youtube search"
    ):

        search_query = query.replace(
            "youtube search",
            "",
            1
        ).strip()

        youtube_search(
            search_query
        )

        return True


    # =====================================================
    # OPEN YOUTUBE
    # =====================================================

    if (
        "open youtube" in query

        or query == "youtube"
    ):

        speak(
            "Opening YouTube."
        )

        webbrowser.open(
            "https://www.youtube.com"
        )

        return True


    # =====================================================
    # OPEN GOOGLE
    # =====================================================

    if (
        "open google" in query

        or query == "google"
    ):

        speak(
            "Opening Google."
        )

        webbrowser.open(
            "https://www.google.com"
        )

        return True


    # =====================================================
    # OPEN WHATSAPP
    # =====================================================

    if (
        "open whatsapp" in query

        or query == "whatsapp"
    ):

        speak(
            "Opening WhatsApp."
        )

        webbrowser.open(
            "https://web.whatsapp.com"
        )

        return True


    # =====================================================
    # OPEN GITHUB
    # =====================================================

    if (
        "open github" in query

        or query == "github"
    ):

        speak(
            "Opening GitHub."
        )

        webbrowser.open(
            "https://github.com"
        )

        return True


    # =====================================================
    # NOTES
    # =====================================================

    if query.startswith(
        "take a note"
    ):

        note = query.replace(
            "take a note",
            "",
            1
        ).strip()

        if note:

            save_note(note)

        else:

            speak(
                "What should I write in the note?"
            )

        return True


    if (
        "read my notes" in query

        or "show my notes" in query
    ):

        read_notes()

        return True


    # =====================================================
    # CALCULATOR
    # =====================================================

    if query.startswith(
        "calculate"
    ):

        expression = query.replace(
            "calculate",
            "",
            1
        ).strip()

        result = calculate_expression(
            expression
        )

        if result is None:

            speak(
                "Sorry, I could not calculate that."
            )

        else:

            speak(
                f"The answer is {result}."
            )

        return True


    # =====================================================
    # QUESTIONS
    # =====================================================

    question_keywords = [

        "java",

        "python",

        "dsa",

        "data structure",

        "data structures",

        "artificial intelligence",

        "what is ai",

        "machine learning",

        "c++",

        "cpp",

        "c plus plus",

        "computer science",

        "api",

        "github"
    ]

    if any(
        keyword in query
        for keyword in question_keywords
    ):

        ask_question(query)

        return True


    # =====================================================
    # UNKNOWN COMMAND
    # =====================================================

    speak(
        "I don't know that command yet. "
        "Try saying time, date, weather, "
        "open YouTube, search Google, "
        "close tab, close window, "
        "calculate, or ask a computer science question."
    )

    return True


# =========================================================
# MAIN
# =========================================================

def main():

    speak(
        "Initializing Jarvis."
    )

    speak(
        "Jarvis is ready. How can I help you?"
    )

    while True:

        query = take_command()

        if not query:

            continue

        should_continue = handle_command(
            query
        )

        if not should_continue:

            break


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    main()