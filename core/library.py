import subprocess
from .exceptions import ProvisioningError

USER = "root"

def __init__(self, user="root"):
    self.user = user

def _execute(self, ip, cmd, description):
        """Interne Hilfsmethode für SSH-Aufrufe mit Error-Handling."""
        target = f"{self.user}@{ip}"
        try:
            # Hier nutzen wir deine gewünschte Logik mit capture_output
            result = subprocess.run(
                ["ssh", target, cmd],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            # Wir sammeln den Fehler ein und werfen unsere eigene Exception
            raise ProvisioningError(
                f"Fehler bei: {description}\n"
                f"Befehl: {cmd}\n"
                f"Ssh-Error: {e.stderr.strip()}"
            )

def install(self, ip, pkg_name, resource):
        """Entscheidet basierend auf der Ressource, wie installiert wird."""
        
        if resource["type"] == "PACKAGE":
            # WEG A: Lokale Datei hochladen und installieren
            print(f"[*] Installiere {pkg_name} lokal von {resource['path']}...")
            remote_tmp = f"/tmp/{pkg_name}.deb"
            
            # 1. Hochladen (SCP)
            subprocess.run(["scp", resource["path"], f"{self.user}@{ip}:{remote_tmp}"], check=True)
            
            # 2. Installieren
            self._execute(ip, f"dpkg -i {remote_tmp} || apt-get install -f -y", 
                          f"Lokale Installation von {pkg_name}")
            
        else:
            # WEG B: Remote über APT laden
            print(f"[*] {pkg_name} nicht lokal gefunden. Nutze APT...")
            self._execute(ip, f"apt-get update && apt-get install -y {pkg_name}", 
                          f"Remote Installation von {pkg_name}")

def execute_custom(self, ip, command):
        """Führt beliebige Post-Install Befehle aus (z.B. NAT-Regeln)."""
        return self._execute(ip, command, "Custom Post-Install Command")

# move to hypervisor    
def get_all_host_vms():
        """
        Fragt den Hypervisor nach allen registrierten VMs.
        """
        # Wir nutzen 'virsh list --all', um auch ausgeschaltete VMs zu sehen
        cmd = ["sudo", "virsh", "list", "--all"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        host_vms = {}
        lines = result.stdout.splitlines()
        
        # Wir überspringen die ersten zwei Header-Zeilen
        for line in lines[2:]:
            parts = line.split()
            if len(parts) >= 2:
                # Bei 'running' ist die ID dabei (parts[0]), 
                # bei 'shut off' ist die ID '-'
                # Der Name ist immer an der zweiten Stelle (Index 1)
                # Der Status ist der Rest der Zeile
                name = parts[1]
                state = " ".join(parts[2:])
                host_vms[name] = state
        return host_vms