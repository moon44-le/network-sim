import subprocess
import time
from .exceptions import ConnectionError

class Hypervisor:
    def __init__(self, name, config=None):
        self.name = name
        self.config = config or {}

    def start(self):
        """Startet die KVM Instanz via Shell-Befehl."""
        if self.is_running():
            print(f"[*] VM '{self.name}' läuft bereits.")
            return

        print(f"[*] Starte VM '{self.name}'...")
        # Hier kommt dein ursprünglicher KVM-Befehl rein
        # Wir nutzen Popen, damit der Prozess im Hintergrund weiterläuft
        cmd = ["./start_vm.sh", self.name] # Oder der direkte qemu-system-x86_64 Befehl
        
        try:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._wait_for_boot()
        except Exception as e:
            raise ConnectionError(f"KVM-Start fehlgeschlagen: {e}")

    def is_running(self):
        """Prüft, ob der Prozess im System existiert."""
        try:
            output = subprocess.check_output(["pgrep", "-f", self.name])
            return len(output) > 0
        except subprocess.CalledProcessError:
            return False

    def _wait_for_boot(self):
        """Wartet kurz, bis die Hardware initialisiert ist."""
        # Ein einfacher Sleep oder ein Ping-Check
        print("[*] Initialisiere Hardware...")
        time.sleep(5)