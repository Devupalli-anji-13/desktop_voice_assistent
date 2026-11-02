
import json
from groq import Groq

from config import GROQ_API_KEY, GROQ_MODEL


client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


def normalize_command(command):
    if client is None:
        raise RuntimeError("GROQ_API_KEY is missing in .env")

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": """
You convert spoken requests into short, safe desktop commands.

Return ONLY a JSON object with one key: "command".

Examples:
"Could you please launch the notepad?" ->
{"command":"open notepad"}

"Can you find Python tutorials on YouTube?" ->
{"command":"search youtube for Python tutorials"}

"Please open my calculator" ->
{"command":"open calculator"}

"Write Hello World in Notepad" ->
{"command":"type Hello World"}

"Close the current tab" ->
{"command":"close tab"}

"Scroll down a little" ->
{"command":"scroll down"}

If the request is not a supported desktop action, return:
{"command":"unknown"}

Supported actions:
open notepad, calculator, paint, file explorer, task manager,
command prompt, powershell, chrome, edge,
open youtube, google, gmail, github, chatgpt,
open whatsapp, instagram, facebook, linkedin, spotify, amazon,
search youtube for [query],
search google for [query],
type [text],
copy, paste, select all, save, undo, redo,
new tab, close tab, switch window, close window,
scroll up, scroll down.

Never return shell commands, executable paths, scripts,
URLs supplied by the user, or arbitrary keyboard instructions.
"""
            },
            {
                "role": "user",
                "content": command
            }
        ],
        temperature=0,
        max_completion_tokens=120
    )

    raw = response.choices[0].message.content.strip()

    try:
        data = json.loads(raw)
        result = data.get("command", "unknown")
        return str(result).strip()
    except (json.JSONDecodeError, AttributeError):
        return "unknown"
