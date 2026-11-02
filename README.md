
# JARVIS Desktop Assistant

Python-based voice-controlled desktop assistant for Windows 10.

## Features

- Futuristic Tkinter interface
- Continuous voice recognition
- Windows SAPI5 voice output
- Groq command interpretation
- KIE GPT-6 Astra general conversations
- Allowlisted application launching
- Website opening and searching
- Dictation into the active application
- Keyboard shortcuts and scrolling
- Spoken confirmation before every desktop action

## Installation

1. Open PowerShell in the project folder.
2. Activate the virtual environment.
3. Install requirements:

   pip install -r requirements.txt

4. Configure GROQ_API_KEY and KIE_API_KEY in .env.
5. Start JARVIS:

   python main.py

## Safety

- Desktop actions require spoken confirmation.
- Only predefined applications and actions are allowed.
- AI-generated responses are never executed as shell commands.
- Move the mouse to the top-left corner to trigger PyAutoGUI failsafe.
