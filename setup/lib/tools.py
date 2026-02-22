import subprocess
import os

class UI:
    
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