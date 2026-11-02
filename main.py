
import tkinter as tk
import threading
import speech_recognition as sr
import pythoncom
import win32com.client
import re

from ai_engine import ask_jarvis
from groq_engine import normalize_command
from desktop_control import build_action


# ==========================================
# JARVIS THEME
# ==========================================

BG = "#030914"
PANEL = "#081626"
CYAN = "#00E5FF"
GREEN = "#35E6A2"
WHITE = "#EAF7FF"
MUTED = "#64859D"
RED = "#FF5368"


class Jarvis:

    def __init__(self, root):

        self.root = root
        self.root.title("J.A.R.V.I.S | AI CORE")
        self.root.geometry("1050x750")
        self.root.minsize(850, 650)
        self.root.configure(bg=BG)

        self.running = True
        self.busy = False
        self.history = []

        self.pending_action = None
        self.input_mode = None

        self.animation_angle = 0

        self.create_ui()

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.shutdown
        )

        self.animate_core()

        self.update_status(
            "INITIALIZING JARVIS",
            CYAN
        )

        threading.Thread(
            target=self.voice_loop,
            daemon=True
        ).start()

    # ======================================
    # USER INTERFACE
    # ======================================

    def create_ui(self):

        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=35, pady=(25, 5))

        tk.Label(
            header,
            text="J.A.R.V.I.S",
            font=("Segoe UI", 30, "bold"),
            fg=CYAN,
            bg=BG
        ).pack(side="left")

        tk.Label(
            header,
            text="PERSONAL AI SYSTEM | GROQ + GPT-6 ASTRA",
            font=("Consolas", 10, "bold"),
            fg=GREEN,
            bg=BG
        ).pack(side="right", pady=15)

        tk.Frame(
            self.root,
            bg="#12374D",
            height=1
        ).pack(fill="x", padx=35, pady=10)

        self.core = tk.Canvas(
            self.root,
            width=360,
            height=310,
            bg=BG,
            highlightthickness=0
        )
        self.core.pack(pady=(5, 0))

        self.status = tk.Label(
            self.root,
            text="SYSTEM STARTING...",
            font=("Consolas", 13, "bold"),
            fg=CYAN,
            bg=BG
        )
        self.status.pack(pady=5)

        self.subtitle = tk.Label(
            self.root,
            text="VOICE SYSTEM INITIALIZING",
            font=("Consolas", 9),
            fg=MUTED,
            bg=BG
        )
        self.subtitle.pack(pady=5)

        conversation_frame = tk.Frame(
            self.root,
            bg=PANEL,
            highlightbackground="#16435A",
            highlightthickness=1
        )
        conversation_frame.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=20
        )

        tk.Label(
            conversation_frame,
            text="LIVE VOICE ACTIVITY",
            font=("Consolas", 10, "bold"),
            fg=CYAN,
            bg=PANEL
        ).pack(anchor="w", padx=18, pady=(12, 5))

        self.chat = tk.Text(
            conversation_frame,
            bg=PANEL,
            fg=WHITE,
            font=("Segoe UI", 11),
            wrap="word",
            relief="flat",
            padx=18,
            pady=10,
            state="disabled",
            height=8
        )
        self.chat.pack(
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        self.chat.tag_config(
            "user",
            foreground=GREEN,
            font=("Consolas", 10, "bold")
        )
        self.chat.tag_config(
            "jarvis",
            foreground=CYAN,
            font=("Consolas", 10, "bold")
        )
        self.chat.tag_config(
            "error",
            foreground=RED
        )

        footer = tk.Frame(self.root, bg=BG)
        footer.pack(fill="x", padx=35, pady=(0, 15))

        tk.Label(
            footer,
            text="VOICE MODE: ACTIVE",
            fg=GREEN,
            bg=BG,
            font=("Consolas", 9, "bold")
        ).pack(side="left")

        tk.Label(
            footer,
            text="SAY 'SHUTDOWN JARVIS' TO EXIT",
            fg=MUTED,
            bg=BG,
            font=("Consolas", 9)
        ).pack(side="right")

    # ======================================
    # ANIMATED CORE
    # ======================================

    def animate_core(self):

        if not self.running:
            return

        self.core.delete("all")

        cx, cy = 180, 150
        pulse = __import__("math").sin(
            self.animation_angle
        ) * 8

        for radius in [125, 105, 85]:
            self.core.create_oval(
                cx - radius - pulse,
                cy - radius - pulse,
                cx + radius + pulse,
                cy + radius + pulse,
                outline="#07506C",
                width=1
            )

        for i in range(12):

            angle = (
                i * 30 + self.animation_angle * 30
            ) * 3.14159 / 180

            import math

            x1 = cx + 110 * math.cos(angle)
            y1 = cy + 110 * math.sin(angle)
            x2 = cx + 120 * math.cos(angle)
            y2 = cy + 120 * math.sin(angle)

            self.core.create_line(
                x1, y1, x2, y2,
                fill=CYAN,
                width=2
            )

        radius = 48 + pulse / 3

        self.core.create_oval(
            cx - radius,
            cy - radius,
            cx + radius,
            cy + radius,
            outline=CYAN,
            width=2,
            fill="#092C43"
        )

        self.core.create_oval(
            cx - 25, cy - 25,
            cx + 25, cy + 25,
            fill="#0B7197",
            outline=CYAN,
            width=2
        )

        self.core.create_text(
            cx, cy,
            text="J",
            fill=WHITE,
            font=("Segoe UI", 28, "bold")
        )

        self.core.create_text(
            cx, 275,
            text="ARTIFICIAL INTELLIGENCE CORE",
            fill=CYAN,
            font=("Consolas", 9, "bold")
        )

        self.animation_angle += 0.08
        self.root.after(40, self.animate_core)

    # ======================================
    # UI HELPERS
    # ======================================

    def post(self, callback, *args):

        if not self.running:
            return

        try:
            self.root.after(
                0,
                lambda: callback(*args)
            )
        except (RuntimeError, tk.TclError):
            pass

    def update_status(self, message, color=CYAN):

        if self.running:
            self.status.config(
                text=message,
                fg=color
            )

    def add_message(self, speaker, message):

        if not self.running:
            return

        self.chat.config(state="normal")

        tag = {
            "YOU": "user",
            "JARVIS": "jarvis",
            "SYSTEM": "error"
        }.get(speaker, "jarvis")

        self.chat.insert("end", f"\n{speaker}\n", tag)
        self.chat.insert("end", str(message) + "\n\n")
        self.chat.see("end")
        self.chat.config(state="disabled")

    # ======================================
    # DESKTOP CONTROL + CONFIRMATION
    # ======================================

    def handle_voice_command(self, question):

        command = question.lower().strip()

        confirm_words = {
            "confirm", "yes", "approve",
            "proceed", "do it", "go ahead",
            "yes confirm"
        }

        cancel_words = {
            "cancel", "no", "stop",
            "never mind", "don't do it"
        }

        # A pending action always takes priority.
        if self.pending_action:

            if command in confirm_words:

                action = self.pending_action
                self.pending_action = None

                try:

                    self.post(
                        self.update_status,
                        "EXECUTING APPROVED ACTION",
                        GREEN
                    )

                    action["run"]()

                    self.input_mode = action.get("next_mode")

                    response = (
                        "Done. "
                        + action["description"]
                        + "."
                    )

                    if action.get("prompt"):
                        response += " " + action["prompt"]

                    return response

                except Exception as error:

                    self.input_mode = None

                    print("ACTION ERROR:", repr(error))

                    return (
                        "I could not complete that action. "
                        + str(error)
                    )

            if command in cancel_words:

                self.pending_action = None

                return "Action cancelled. Nothing was changed."

            return (
                "I have a pending action: "
                + self.pending_action["description"]
                + ". Please say Confirm or Cancel."
            )

        if command in cancel_words:
            self.input_mode = None
            return "Cancelled."

        # Try local matching first.
        action = build_action(
            question,
            input_mode=self.input_mode
        )

        # Groq helps understand natural phrases that local
        # matching did not recognize. Its output is still
        # checked against our local allowlist.
        if action is None and self.input_mode is None:

            control_words = (
                "open", "launch", "start", "go to", "run",
                "search", "find", "type", "write",
                "copy", "paste", "save", "undo",
                "redo", "scroll", "switch", "close"
            )

            if any(word in command for word in control_words):

                try:
                    normalized = normalize_command(question)

                    if normalized != "unknown":
                        action = build_action(normalized)

                except Exception as error:
                    print("GROQ COMMAND ERROR:", repr(error))

        if action:

            self.pending_action = action

            return (
                "Permission required. "
                + action["description"]
                + ". Should I proceed? Say Confirm or Cancel."
            )

        if self.input_mode == "type_text":
            return "Please tell me the text you want me to type."

        if self.input_mode in ("youtube_search", "google_search"):
            return "Please tell me what you want me to search for."

        return None

    # ======================================
    # VOICE ENGINE
    # ======================================

    def voice_loop(self):

        voice = None
        com_initialized = False

        try:

            pythoncom.CoInitialize()
            com_initialized = True

            voice = win32com.client.Dispatch("SAPI.SpVoice")
            voice.Rate = 0
            voice.Volume = 100

            recognizer = sr.Recognizer()
            recognizer.pause_threshold = 0.8
            recognizer.dynamic_energy_threshold = True

            def speak(text):

                if not text or not self.running:
                    return

                try:
                    self.post(
                        self.update_status,
                        "JARVIS IS SPEAKING",
                        CYAN
                    )

                    print("SPEAKING:", text)
                    voice.Speak(str(text), 0)

                except Exception as error:
                    print("SPEECH ERROR:", repr(error))

            with sr.Microphone() as source:

                self.post(
                    self.update_status,
                    "CALIBRATING MICROPHONE",
                    CYAN
                )

                recognizer.adjust_for_ambient_noise(
                    source,
                    duration=1
                )

                greeting = (
                    "Hello! I am JARVIS, your personal "
                    "artificial intelligence assistant."
                )

                self.post(
                    self.add_message,
                    "JARVIS",
                    greeting
                )
                speak(greeting)

                while self.running:

                    try:

                        self.post(
                            self.update_status,
                            "LISTENING TO YOUR VOICE",
                            GREEN
                        )

                        audio = recognizer.listen(
                            source,
                            timeout=2,
                            phrase_time_limit=12
                        )

                        self.post(
                            self.update_status,
                            "UNDERSTANDING YOUR COMMAND",
                            CYAN
                        )

                        question = recognizer.recognize_google(
                            audio,
                            language="en-IN"
                        ).strip()

                        if not question:
                            continue

                        print("YOU:", question)

                        self.post(
                            self.add_message,
                            "YOU",
                            question
                        )

                        command = question.lower().strip()

                        if any(item in command for item in (
                            "shutdown jarvis",
                            "close jarvis",
                            "exit jarvis"
                        )):

                            goodbye = "Shutting down JARVIS. Goodbye!"

                            self.post(
                                self.add_message,
                                "JARVIS",
                                goodbye
                            )

                            speak(goodbye)
                            self.post(self.shutdown)
                            return

                        # Handle desktop actions first.
                        action_response = self.handle_voice_command(
                            question
                        )

                        if action_response:

                            self.post(
                                self.add_message,
                                "JARVIS",
                                action_response
                            )

                            speak(action_response)
                            continue

                        # General questions go to KIE.
                        self.post(
                            self.update_status,
                            "GPT-6 ASTRA IS THINKING",
                            CYAN
                        )

                        answer = ask_jarvis(
                            question,
                            None,
                            self.history
                        )

                        answer = str(answer).strip()

                        if not answer:
                            answer = "I could not generate an answer."

                        self.history.extend([
                            {"role": "user", "content": question},
                            {"role": "assistant", "content": answer}
                        ])

                        self.post(
                            self.add_message,
                            "JARVIS",
                            answer
                        )

                        speak(answer)

                    except sr.WaitTimeoutError:
                        continue

                    except sr.UnknownValueError:
                        self.post(
                            self.update_status,
                            "DID NOT CATCH THAT - LISTENING",
                            MUTED
                        )
                        continue

                    except sr.RequestError as error:

                        self.post(
                            self.update_status,
                            "SPEECH RECOGNITION ERROR",
                            RED
                        )

                        self.post(
                            self.add_message,
                            "SYSTEM",
                            str(error)
                        )

                        threading.Event().wait(3)

                    except Exception as error:

                        print("JARVIS ERROR:", repr(error))

                        self.post(
                            self.add_message,
                            "SYSTEM",
                            str(error)
                        )

                        self.post(
                            self.update_status,
                            "ERROR - RETRYING",
                            RED
                        )

                        threading.Event().wait(2)

        except Exception as error:

            print("VOICE INITIALIZATION ERROR:", repr(error))

            self.post(
                self.update_status,
                "VOICE SYSTEM INITIALIZATION FAILED",
                RED
            )

            self.post(
                self.add_message,
                "SYSTEM",
                str(error)
            )

        finally:

            self.busy = False

            try:
                if voice:
                    voice.Speak("", 3)
            except Exception:
                pass

            if com_initialized:
                try:
                    pythoncom.CoUninitialize()
                except Exception:
                    pass

    # ======================================
    # SHUTDOWN
    # ======================================

    def shutdown(self):

        if not self.running:
            return

        self.running = False

        try:
            self.root.destroy()
        except tk.TclError:
            pass


# ==========================================
# START APPLICATION
# ==========================================

if __name__ == "__main__":

    root = tk.Tk()
    app = Jarvis(root)
    root.mainloop()
