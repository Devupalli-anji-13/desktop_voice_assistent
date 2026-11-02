from groq_engine import understand_command

while True:
    command = input("You: ")

    if command.lower() == "exit":
        break

    try:
        print("JARVIS:", understand_command(command))
    except Exception as error:
        print("Error:", error)