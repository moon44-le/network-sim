import subprocess
import os
import config

class UI:
    
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    RESET = "\033[0m"

    @staticmethod
    def clear():
        command = "cls" if os.name == "nt" else "clear"
        subprocess.run([command])

    @staticmethod
    def header(text):
        print(f"{UI.GREEN}=== {text} ==={UI.RESET}\n")

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
    def delete(vm_name):
        subprocess.run(
            ["virsh", "destroy", vm_name],
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL)
        subprocess.run(
            ["virsh", "undefine", vm_name, "--remove-all-storage"], 
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True)
        
    @staticmethod
    def create(vm_config: dict, iso_path: str):
        """
        Erstellt eine VM basierend auf dem Dictionary aus der YAML-Datei.
        """
        print(f"Erstelle VM '{vm_config['name']}'...")
        
        # Wir bauen das Argument-Array (List) für subprocess
        cmd = [
            "virt-install",
            "--name", vm_config['name'],
            "--ram", str(vm_config['ram']),
            "--vcpus", str(vm_config['vcpus']),
            "--os-variant", vm_config.get('os', 'debian11'),
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