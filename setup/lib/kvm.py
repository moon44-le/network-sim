import subprocess
import os
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
        
 #   @staticmethod
 #   def create(vm_config: dict, iso_path: str):
 #       print(f"Erstelle VM '{vm_config['name']}'...")
        
    @staticmethod
    def create(vm_config: dict):
        
        public_key = KVM.get_public_key()
        if not public_key:
            return False
        
        hostname = vm_config['hostname']
        iso_path = vm_config['iso_path']
        
        # Preseed-Kommandos für die Automatisierung
        # Wir sagen dem Installer: Installiere SSH und lege den Key ab.
        extra_args = (
            f"pkgsel/include=openssh-server,sudo "
            f"preseed/late_command=\"in-target mkdir -p /home/kvm-admin/.ssh; "
            f"in-target /bin/sh -c 'echo {public_key} > /home/kvm-admin/.ssh/authorized_keys'; "
            f"in-target chown -R kvm-admin:kvm-admin /home/kvm-admin/.ssh; "
            f"in-target chmod 700 /home/kvm-admin/.ssh; "
            f"in-target chmod 600 /home/kvm-admin/.ssh/authorized_keys\""
        )

        cmd = [
            "sudo", "virt-install",
            "--name", hostname,
            "--ram", str(vm_config['ram']),
            "--vcpus", str(vm_config['vcpus']),
            "--disk", f"path=/var/lib/libvirt/images/{hostname}.qcow2,size={vm_config['disk']}",
            "--os-variant", "debian12",
            "--location", iso_path,
            "--network", "network=default",
            "--graphics", "none",
            "--extra-args", f"console=ttyS0,115200n8 serial {extra_args}"
        ]

        try:
            # Wir führen den Befehl aus und unterdrücken stdout, 
            # wollen aber stderr sehen, falls die Installation scheitert.
            subprocess.run(cmd, check=True, stderr=subprocess.PIPE, text=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"\033[31mFehler bei virt-install: {e.stderr}\033[0m")
            return False
        


    def get_public_key():
        # Pfad zum Standard-Key (id_rsa.pub oder id_ed25519.pub)
        key_path = os.path.expanduser("~/.ssh/id_rsa.pub")
        
        # Falls id_rsa nicht existiert, probieren wir ed25519 (moderner Standard)
        if not os.path.exists(key_path):
            key_path = os.path.expanduser("~/.ssh/id_ed25519.pub")

        try:
            with open(key_path, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            print(f"[!] Fehler: Kein Public Key unter {key_path} gefunden!")
            return None