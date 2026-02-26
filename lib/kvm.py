import subprocess
import os
import shutil
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
        


    @staticmethod
    def create(vm_config: dict):
        """
        Erstellt eine KVM aus einem Debian-Cloud-Image.
        vm_config: {
            "hostname": "mein-server",
            "ram": 2048,
            "vcpus": 2,
            "disk": 20, # in GB
            "networks": ["default", "br-intern"], # Liste von Netzwerken
            "base_image": "/pfad/zu/debian-12-generic-amd64.qcow2"
        }
        """
        hostname = vm_config['hostname']
        storage_pool = "/var/lib/libvirt/images"
        target_disk = f"{storage_pool}/{hostname}.qcow2"
        seed_iso = f"{storage_pool}/{hostname}-seed.iso"

        print(f"[*] Starte Deployment für {hostname}...")
        KVM.prepare_disk(vm_config)

        # 1. Disk vorbereiten (Kopieren & Resize)
        try:
            shutil.copy(vm_config['base_image'], target_disk)
            subprocess.run(["sudo", "qemu-img", "resize", target_disk, f"{vm_config['disk']}G"], check=True)
            # Wichtig: Berechtigungen für libvirt setzen
            subprocess.run(["sudo", "chown", "libvirt-qemu:kvm", target_disk], check=True)
        except Exception as e:
            print(f"[-] Fehler bei Disk-Vorbereitung: {e}")
            return False

        # 2. Cloud-Init (seed.iso) erstellen
        if not KVM._generate_seed_iso(hostname, seed_iso):
            return False

        # 3. Netzwerk-Parameter dynamisch aufbauen
        # In Python nutzen wir List-Comprehension (ähnlich wie array_map in PHP)
        net_args = []
        for net in vm_config['networks']:
            if net == "default":
                net_args.extend(["--network", "network=default"])
            else:
                net_args.extend(["--network", f"bridge={net}"])

        # 4. virt-install Befehl
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
        ] + net_args # Hängt die Netzwerk-Argumente an die Liste an

        try:
            subprocess.run(cmd, check=True)
            print(f"[+] VM '{hostname}' erfolgreich deployt.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[-] Fehler bei virt-install: {e}")
            return False

    @staticmethod
    def create_seed(vm_config: dict):
        """
        Erstellt die seed.iso für Cloud-Init.
        In PHP würde man hier ein assoziatives Array (Dictionary) validieren.
        """
        hostname = vm_config['hostname']
        # Pfad, wo die ISO landen soll
        seed_path = f"/var/lib/libvirt/images/{hostname}-seed.iso"
        
        # 1. User-Data (User & SSH-Key)
        public_key = KVM.get_public_key()
        user_data = f"""#cloud-config
hostname: {hostname}
users:
  - name: kvm-admin
    sudo: ALL=(ALL) NOPASSWD:ALL
    groups: users, sudo
    shell: /bin/bash
    ssh_authorized_keys:
      - {public_key}
packages:
  - qemu-guest-agent
  - openssh-server
"""

        # 2. Meta-Data (Instanz-ID)
        meta_data = f"instance-id: {hostname}\nlocal-hostname: {hostname}"

        # 3. Network-Config (V2 Format)
        # Wir gehen davon aus: 1. Interface (ens3) = DHCP/Default, 2. Interface (ens4) = br-intern
        network_config = "version: 2\nethernets:\n  ens3:\n    dhcp4: true\n"
        
        # Falls es der DHCP-Server ist, braucht er eine statische IP auf ens4
        if vm_config.get('role') == 'gateway':
            static_ip = vm_config.get('static_ip_intern', '192.168.1.1/24')
            network_config += f"  ens4:\n    addresses: [{static_ip}]\n"

        # Temporäre Dateien schreiben
        try:
            with open("user-data", "w") as f: f.write(user_data)
            with open("meta-data", "w") as f: f.write(meta_data)
            with open("network-config", "w") as f: f.write(network_config)

            print(f"[*] Generiere Seed-ISO für {hostname}...")
            # Der Befehl cloud-localds kombiniert alles zur ISO
            subprocess.run([
                "cloud-localds", 
                "-n", "network-config", 
                seed_path, 
                "user-data", 
                "meta-data"
            ], check=True)

            # Aufräumen (PHP: unlink)
            for tmp_file in ["user-data", "meta-data", "network-config"]:
                if os.path.exists(tmp_file):
                    os.remove(tmp_file)
            
            print(f"[+] Seed-ISO erstellt unter: {seed_path}")
            return seed_path

        except Exception as e:
            print(f"[-] Fehler beim Erstellen der Seed-ISO: {e}")
            return None
        
    @staticmethod
    def generate_cloud_init_config(hostname, output_path):
        """
        Erstellt die user-data und meta-data und baut daraus die seed.iso
        """
        public_key = KVM.get_public_key()
        if not public_key:
            return False

        # Cloud-Init Konfiguration (YAML-Format)
        user_data = f"""#cloud-config
hostname: {hostname}
manage_etc_hosts: true
users:
  - name: kvm-admin
    sudo: ALL=(ALL) NOPASSWD:ALL
    groups: users, sudo
    shell: /bin/bash
    ssh_authorized_keys:
      - {public_key}
chpasswd:
  list: |
     kvm-admin:password  # Optional: Standardpasswort setzen
  expire: False
ssh_pwauth: True
packages:
  - qemu-guest-agent
  - openssh-server
"""
        meta_data = f"instance-id: {hostname}\nlocal-hostname: {hostname}"

        # Temporäre Dateien schreiben und mit genisoimage/mkisofs zur ISO machen
        try:
            with open("user-data", "w") as f: f.write(user_data)
            with open("meta-data", "w") as f: f.write(meta_data)
            
            # Befehl zum Erstellen der seed.iso (Label MAPPING ist wichtig für Cloud-Init)
            cmd = [
                "genisoimage", "-output", output_path,
                "-volid", "cidata", "-joliet", "-rock",
                "user-data", "meta-data"
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Aufräumen
            os.remove("user-data")
            os.remove("meta-data")
            return True
        except Exception as e:
            print(f"Fehler beim Erstellen der seed.iso: {e}")
            return False
        
    @staticmethod
    def prepare_disk(vm_config: dict):
        hostname = vm_config['hostname']
        base_image = vm_config['base_image'] # z.B. "./data/debian-12..."
        target_path = f"/var/lib/libvirt/images/{hostname}.qcow2"

        try:
            print(f"[*] Kopiere Image nach {target_path}...")
            # Wir nutzen sudo cp, um Schreibrechte in /var/lib/libvirt/images zu haben
            subprocess.run(["sudo", "cp", base_image, target_path], check=True)

            print(f"[*] Passe Besitzer für Libvirt an...")
            # WICHTIG: Libvirt muss die Datei lesen/schreiben dürfen
            # Unter Debian/Ubuntu ist der User meist libvirt-qemu
            subprocess.run(["sudo", "chown", "libvirt-qemu:libvirt-qemu", target_path], check=True)
            subprocess.run(["sudo", "chmod", "660", target_path], check=True)

            # Resize (wie besprochen)
            size = f"{vm_config['disk']}G"
            subprocess.run(["sudo", "qemu-img", "resize", target_path, size], check=True)
            
            return target_path
        except subprocess.CalledProcessError as e:
            print(f"\033[31m[FEHLER] Berechtigungsproblem oder cp fehlgeschlagen: {e}\033[0m")
            return None