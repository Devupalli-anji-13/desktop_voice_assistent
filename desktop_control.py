
import subprocess
import webbrowser
from urllib.parse import quote_plus

import pyautogui
import pyperclip


# Emergency stop: move the mouse to the top-left corner.
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.3


APPLICATIONS = {
    "notepad": ["notepad.exe"],
    "calculator": ["calc.exe"],
    "paint": ["mspaint.exe"],
    "file explorer": ["explorer.exe"],
    "task manager": ["taskmgr.exe"],
    "command prompt": ["cmd.exe"],
    "powershell": ["powershell.exe"],
    "chrome": ["chrome.exe"],
    "edge": ["msedge.exe"],
}

WEBSITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "github": "https://github.com",
    "chatgpt": "https://chatgpt.com",
    "whatsapp": "https://web.whatsapp.com",
    "instagram": "https://www.instagram.com",
    "facebook": "https://www.facebook.com",
    "linkedin": "https://www.linkedin.com",
    "spotify": "https://open.spotify.com",
    "amazon": "https://www.amazon.in",
}


def proposal(description, function, next_mode=None, prompt=None):
    return {
        "description": description,
        "run": function,
        "next_mode": next_mode,
        "prompt": prompt
    }


def build_action(command, input_mode=None):

    command = command.lower().strip()

    # A new open command exits the previous follow-up mode.
    if command.startswith((
        "open ", "launch ", "start ", "go to ", "run "
    )):
        input_mode = None

    # Text dictated after Notepad has been opened.
    if input_mode == "type_text":

        text = command

        for prefix in ("write ", "type ", "enter ", "dictate "):
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
                break

        if not text:
            return None

        def paste_text():
            pyperclip.copy(text)
            pyautogui.hotkey("ctrl", "v")

        return proposal(
            f"Type this text into the active application: {text}",
            paste_text,
            next_mode="type_text",
            prompt="What else would you like me to type?"
        )

    # Search follow-up after opening Google or YouTube.
    if input_mode in ("youtube_search", "google_search"):

        query = command

        for prefix in ("search for ", "search ", "find "):
            if query.startswith(prefix):
                query = query[len(prefix):].strip()
                break

        if not query:
            return None

        if input_mode == "youtube_search":
            url = (
                "https://www.youtube.com/results?search_query="
                + quote_plus(query)
            )
            description = f"Search YouTube for {query}"
        else:
            url = (
                "https://www.google.com/search?q="
                + quote_plus(query)
            )
            description = f"Search Google for {query}"

        return proposal(
            description,
            lambda: webbrowser.open(url),
            next_mode=input_mode,
            prompt="Would you like to search for something else?"
        )

    # Opening applications.
    for prefix in ("open ", "launch ", "start ", "go to ", "run "):

        if command.startswith(prefix):

            target = command[len(prefix):].strip()

            for suffix in (" for me", " now", " please"):
                if target.endswith(suffix):
                    target = target[:-len(suffix)].strip()

            if target in APPLICATIONS:

                if target == "notepad":
                    next_mode = "type_text"
                    prompt = (
                        "Notepad is ready. "
                        "What would you like me to write?"
                    )
                else:
                    next_mode = None
                    prompt = None

                return proposal(
                    f"Open {target}",
                    lambda: subprocess.Popen(APPLICATIONS[target]),
                    next_mode,
                    prompt
                )

            if target in WEBSITES:

                if target == "youtube":
                    next_mode = "youtube_search"
                    prompt = (
                        "YouTube is open. "
                        "What would you like me to search for?"
                    )
                elif target == "google":
                    next_mode = "google_search"
                    prompt = (
                        "Google is open. "
                        "What would you like me to search for?"
                    )
                else:
                    next_mode = None
                    prompt = None

                return proposal(
                    f"Open {target}",
                    lambda: webbrowser.open(WEBSITES[target]),
                    next_mode,
                    prompt
                )

            return None

    # Direct search commands.
    search_prefixes = {
        "search youtube for ": "youtube",
        "search on youtube for ": "youtube",
        "youtube search for ": "youtube",
        "search google for ": "google",
        "search web for ": "google",
        "search the web for ": "google",
        "google search for ": "google",
    }

    for prefix, engine in search_prefixes.items():

        if command.startswith(prefix):

            query = command[len(prefix):].strip()

            if not query:
                return None

            if engine == "youtube":
                url = (
                    "https://www.youtube.com/results?search_query="
                    + quote_plus(query)
                )
            else:
                url = (
                    "https://www.google.com/search?q="
                    + quote_plus(query)
                )

            return proposal(
                f"Search {engine.title()} for {query}",
                lambda: webbrowser.open(url)
            )

    # Typing directly into the currently active window.
    for prefix in ("type ", "write "):

        if command.startswith(prefix):

            text = command[len(prefix):].strip()

            if text:
                def type_text():
                    pyperclip.copy(text)
                    pyautogui.hotkey("ctrl", "v")

                return proposal(
                    f"Type this text into the active window: {text}",
                    type_text
                )

    # Fixed, allowlisted keyboard shortcuts.
    shortcuts = {
        "copy": ("ctrl", "c"),
        "paste": ("ctrl", "v"),
        "select all": ("ctrl", "a"),
        "save": ("ctrl", "s"),
        "undo": ("ctrl", "z"),
        "redo": ("ctrl", "y"),
        "new tab": ("ctrl", "t"),
        "close tab": ("ctrl", "w"),
        "switch window": ("alt", "tab"),
        "close window": ("alt", "f4"),
    }

    if command in shortcuts:
        keys = shortcuts[command]

        return proposal(
            f"Perform keyboard shortcut: {command}",
            lambda: pyautogui.hotkey(*keys)
        )

    # Scrolling.
    if command in ("scroll down", "scroll down page"):
        return proposal(
            "Scroll down",
            lambda: pyautogui.scroll(-5)
        )

    if command in ("scroll up", "scroll up page"):
        return proposal(
            "Scroll up",
            lambda: pyautogui.scroll(5)
        )

    return None
