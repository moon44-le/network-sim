import subprocess

class NetworkSimError(Exception): pass
class ProvisioningError(NetworkSimError): pass

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

# --- Anwendung in der Gateway-Logik ---

def setup_gateway(ip):
    target = f"root@{ip}"
    
    # Nah am Befehl: Jeder Aufruf prüft sich selbst
    safe_execute(["ssh", target, "apt-get update"], "Update der Paketquellen")
    safe_execute(["ssh", target, "apt-get install -y iptables"], "Installation von iptables")