import subprocess
import os
import readline

class UI:

    WHITE = "\033[37m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    RESET = "\033[0m"

    @staticmethod
    def clear():
        command = "cls" if os.name == "nt" else "clear"
        subprocess.run([command])

    @staticmethod
    def header(text):
        print(f"{UI.GREEN}=== {text} ==={UI.RESET}\n")

    def setup_shell_history():
        history_file = os.path.expanduser("~/.kvm_manager_history")
        # 1. Versuche, die alte History zu laden
        if os.path.exists(history_file):
            try:
                readline.read_history_file(history_file)
            except Exception:
                pass # Falls die Datei korrupt ist

        # 2. Automatisch beim Beenden speichern
        import atexit
        atexit.register(readline.write_history_file, history_file)

        # 3. (Optional) Tab-Completion aktivieren (sehr komfortabel!)
        readline.parse_and_bind("tab: complete")