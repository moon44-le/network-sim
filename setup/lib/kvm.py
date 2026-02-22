import subprocess

from lib.tools import UI
from lib.inventory import Inventory

class KVM:

    @staticmethod
    def is_installed(vm_name):
        check_cmd = ["virsh", "list", "--all", "--name"]
        
        try:
            result = subprocess.run(check_cmd, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"\033[31mCalledProcessError: {e.stderr}\033[0m")
            return False
        except Exception as e:
            print(f"Exception in KVM.is_installed: {e}")
        
        installed_vms = result.stdout.splitlines()
        return vm_name in [name.strip() for name in installed_vms]

    @staticmethod
    def destroy(vm_name):
        """Stoppt die VM hart, falls sie läuft."""
        host_vms = Inventory.get_all_host_vms()
        state = host_vms.get(vm_name, "").lower()

        if "running" in state:
            print(f"[*] Stoppe laufende VM: {vm_name}...")
            cmd = ["sudo", "virsh", "destroy", vm_name]
            return subprocess.run(cmd, capture_output=True).returncode == 0
        
        return True # War schon aus oder existiert nicht

    @staticmethod
    def undefine(vm_name):
        """
        Kaskadiertes Löschen:
        1. Existenz-Check
        2. Automatischer Stop (destroy), falls nötig
        3. Definition entfernen
        """
        host_vms = Inventory.get_all_host_vms()

        # 1. Existenz-Check
        if vm_name not in host_vms:
            print(f"[!] Abbruch: VM '{vm_name}' existiert gar nicht.")
            return False
        
        # 2. Automatisches Kaskadieren: Wenn sie läuft, erst stoppen
        state = host_vms[vm_name].lower()
        if "running" in state:
            
            print(f"[*] VM '{vm_name}' läuft noch. Kaskadiere zu destroy...")
            if not KVM.destroy(vm_name):
                print(f"[!] Fehler beim Stoppen von '{vm_name}'. Löschen abgebrochen.")
                return False

        # 3. Das eigentliche Undefine
        print(f"[*] Lösche VM-Definition und Storage für: {vm_name}...")
        cmd = ["sudo", "virsh", "undefine", vm_name, "--remove-all-storage"]
        success = subprocess.run(cmd, capture_output=True).returncode == 0
        
        if success:
            print(f"[+] VM '{vm_name}' erfolgreich entfernt.")
        return success
    
    @staticmethod
    def start(vm_name):
        print(f"[*] Starte VM: {vm_name}...")
        cmd = ["sudo", "virsh", "start", vm_name]
        return subprocess.run(cmd, capture_output=True).returncode == 0
        
    @staticmethod
    def create(vm_config: dict, iso_path: str):
        print(f"Erstelle VM '{vm_config['name']}'...")
        
        # Wir bauen das Argument-Array (List) für subprocess
        cmd = [
            "virt-install",
            "--name", vm_config['hostname'],
            "--ram", str(vm_config['ram']),
            "--vcpus", str(vm_config['vcpus']),
            "--os-variant", vm_config.get('os', 'debian12'),
            "--disk", f"size={vm_config.get('disk', 10)},format=qcow2",
            "--cdrom", iso_path,
            "--network", "network=default",
            "--graphics", "vnc",
            "--noautoconsole",
            "--wait", "0" # Damit das Skript nicht blockiert, bis die Installation fertig ist
        ]

        try:
            # Wir führen den Befehl aus und unterdrücken stdout, 
            # wollen aber stderr sehen, falls die Installation scheitert.
            subprocess.run(cmd, check=True, stderr=subprocess.PIPE, text=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"\033[31mFehler bei virt-install: {e.stderr}\033[0m")
            return False