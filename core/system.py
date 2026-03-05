import subprocess

def run(cmd, description="Befehl"):
    """Zentrale Funktion für alle lokalen Shell-Befehle."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, shell=isinstance(cmd, str))
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"[!] Fehler bei {description}: {e.stderr or e.stdout}")
        return None