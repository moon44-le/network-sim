import subprocess
import os
import shutil
from lib.tools import UI
from lib.inventory import Inventory


class KVM:

    STORAGE_POOL = "/var/lib/libvirt/images"

    @staticmethod
    def is_installed(vm_name):
        check_cmd = ["virsh", "list", "--all", "--name"]
        
        try:
            result = subprocess.run(check_cmd, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"CalledProcessError: {e.stderr}")
            return False
        except Exception as e:
            print(f"Exception: {e}")
        
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

    def get_public_key():
        key_path = os.path.expanduser("~/.ssh/id_rsa.pub")
        if not os.path.exists(key_path):
            key_path = os.path.expanduser("~/.ssh/id_ed25519.pub")
        try:
            with open(key_path, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            print(f"[!] Fehler: Kein Public Key unter {key_path} gefunden!")
            return None
        
    @staticmethod
    def create(vm_config: dict):
        hostname = vm_config['hostname']
        print(f"[*] Starte Deployment für {hostname}...")

        # 1. Disk vorbereiten
        if not KVM.prepare_disk(vm_config):
            return False

        # 2. Cloud-Init (seed.iso) vorbereiten
        if not KVM._generate_and_move_seed_iso(vm_config):
            return False

        # Pfade für virt-install (direkt aus dem Pool gebildet)
        target_disk = f"{KVM.STORAGE_POOL}/{hostname}.qcow2"
        seed_iso = f"{KVM.STORAGE_POOL}/{hostname}-seed.iso"

        # 3. Netzwerk-Parameter (PHP: array_merge Logik)
        net_args = []
        for net in vm_config['networks']:
            if net == "default":
                net_args.extend(["--network", "network=default"])
            else:
                net_args.extend(["--network", f"bridge={net}"])

        # 4. virt-install
        cmd = [
            "sudo", "virt-install",
            "--name", hostname,
            "--ram", str(vm_config['ram']),
            "--vcpus", str(vm_config['vcpus']),
            "--disk", f"path={target_disk},format=qcow2",
            "--disk", f"path={seed_iso},device=cdrom",
            "--os-variant", "debian12",
            "--graphics", "none",
            "--import",
            "--noautoconsole"
        ] + net_args

        try:
            subprocess.run(cmd, check=True)
            print(f"[+] VM '{hostname}' erfolgreich deployt.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[-] Fehler bei virt-install: {e}")
            return False

    @staticmethod
    def prepare_disk(vm_config):
        target_path = f"{KVM.STORAGE_POOL}/{vm_config['hostname']}.qcow2"
        try:
            subprocess.run(["sudo", "cp", vm_config['base_image'], target_path], check=True)
            subprocess.run(["sudo", "qemu-img", "resize", target_path, f"{vm_config['disk']}G"], check=True)
            subprocess.run(["sudo", "chown", "libvirt-qemu:libvirt-qemu", target_path], check=True)
            return True
        except Exception as e:
            print(f"[-] Disk-Fehler: {e}")
            return False

    @staticmethod
    def _generate_and_move_seed_iso(vm_config):
        """Bildet den Zielpfad ebenfalls intern."""
        hostname = vm_config['hostname']
        target_iso = f"{KVM.STORAGE_POOL}/{hostname}-seed.iso"
        local_iso = f"./{hostname}-seed.iso"
        
        # Public Key einbinden
        public_key = KVM.get_public_key()
        
        user_data = f"#cloud-config\nhostname: {hostname}\nusers:\n  - name: kvm-admin\n    sudo: ALL=(ALL) NOPASSWD:ALL\n    ssh_authorized_keys:\n      - {public_key}\n"
        meta_data = f"instance-id: {hostname}\nlocal-hostname: {hostname}"

        try:
            with open("user-data", "w") as f: f.write(user_data)
            with open("meta-data", "w") as f: f.write(meta_data)
            
            subprocess.run(["cloud-localds", local_iso, "user-data", "meta-data"], check=True)
            subprocess.run(["sudo", "mv", local_iso, target_iso], check=True)
            subprocess.run(["sudo", "chown", "libvirt-qemu:libvirt-qemu", target_iso], check=True)
            
            for f in ["user-data", "meta-data"]: os.remove(f)
            return True
        except Exception as e:
            print(f"[-] Seed-Fehler: {e}")
            return False
        
 #   @staticmethod
    #def prepare_disk(vm_config: dict):
    #    hostname = vm_config['hostname']
    #    base_image = vm_config['base_image']
    #   target_path = f"/var/lib/libvirt/images/{hostname}.qcow2"

#        try:
            # 1. Kopieren via SUDO (da Python selbst nicht in den Zielordner schreiben darf)
#            print(f"[*] Kopiere Image nach {target_path}...")
#            subprocess.run(["sudo", "cp", base_image, target_path], check=True)
#
#            # 2. Resize via SUDO
#            print(f"[*] Vergrößere Disk auf {vm_config['disk']}G...")
#            subprocess.run(["sudo", "qemu-img", "resize", target_path, f"{vm_config['disk']}G"], check=True)

            # 3. Besitzer anpassen (Damit QEMU/Libvirt die Datei nutzen kann)
#            print(f"[*] Setze Berechtigungen für libvirt-qemu...")
#            subprocess.run(["sudo", "chown", "libvirt-qemu:libvirt-qemu", target_path], check=True)
#            subprocess.run(["sudo", "chmod", "660", target_path], check=True)
            
#            return target_path
#        except subprocess.CalledProcessError as e:
#            print(f"\033[31m[-] Fehler bei der Disk-Operation: {e}\033[0m")
#            return None