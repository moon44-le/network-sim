import subprocess

class NetworkSimError(Exception): pass
class ProvisioningError(NetworkSimError): pass
class HypervisorError(NetworkSimError): pass

def safe_execute(cmd_list, description):
    """
    Der Wrapper: Er ist nah am Befehl und 'übersetzt' 
    Systemfehler in deine Logik-Fehler.
    """
    try:
        print(f"[*] {description}...")
        # check=True sorgt für das 'Throw early'
        return subprocess.run(cmd_list, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        # Hier veredeln wir den Fehler mit Kontext
        raise ProvisioningError(
            f"Fehler bei: {description}\n"
            f"Befehl: {' '.join(cmd_list)}\n"
            f"Exit-Code: {e.returncode}\n"
            f"Fehlermeldung: {e.stderr.strip()}"
        )