import subprocess
import time
from .exceptions import ConnectionError

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


def start_node(name):
    return safe_execute(["sudo", "virsh", "start", name])

def undefine_node(name):
    # Kaskadierung (Stoppen vor Löschen) macht jetzt der Orchestrator!
    return safe_execute(["sudo", "virsh", "undefine", name, "--remove-all-storage"])

def copy_base_image(source, target):
    safe_execute(["sudo", "cp", source, target])
    safe_execute(["sudo", "chown", "libvirt-qemu:libvirt-qemu", target])

def create_cloud_init_iso(name, user_data_path, target_iso):
    # cloud-localds Aufruf...
    pass