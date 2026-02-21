import yaml
import shlex
import subprocess # Für lokale Tests, später durch SSH (paramiko) ersetzbar

from pathlib import Path

class UI:
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    RESET = "\033[0m"

def is_vm_installed(vm_name):
    # --name gibt nur die Namen zurück, --all zeigt auch ausgeschaltete VMs
    check_cmd = ["virsh", "list", "--all", "--name"]
    result = subprocess.run(check_cmd, capture_output=True, text=True)
    installed_vms = result.stdout.splitlines()
    return vm_name in [name.strip() for name in installed_vms]

def create_kvm_command(config_path):
    # 1. YAML Datei laden
    with open(config_path, 'r') as file:
        data = yaml.safe_load(file)
    
    vm          = data['vm_metadata']
    safe_name   = shlex.quote(vm['name'])
    safe_ram    = shlex.quote(str(vm['ram_mb']))
    safe_vcpus  = shlex.quote(str(vm['vcpus']))
    safe_disk   = shlex.quote(str(vm['disk_gb']))
    
    # 4. Den finalen Befehl zusammenbauen (Der "Stream-String")
    # Wir nutzen virt-install als Beispiel-Tool auf dem Zielserver
    
    final_cmd = [
        "virt-install",
        "--name",       f"{safe_name}",
        "--memory",     f"{safe_ram}",
        "--vcpus",      f"{safe_vcpus}",
        "--disk",       f"size={safe_disk}",
        "--os-variant", f"{vm['os_type']}",
        "--graphics",   "none",
        "--import",
        "--noautoconsole"
    ]
    vm['generated_cmd']     = final_cmd
    vm['safe_name']         = safe_name
    return vm

# --- HAUPTPROGRAMM ---
if __name__ == "__main__":
    config_file = './setup/vm_config.yaml'
    print(f"--- Lade Konfiguration aus {config_file} ---")
    try:
        vm = create_kvm_command(config_file)
    except FileNotFoundError:
        current_dir = Path.cwd()
        print(f"Fehler: Die Datei '{config_file}' wurde nicht gefunden.")
        print(f"Du befindest dich gerade in: {current_dir}")
        script_dir = Path(__file__).parent
        print(f"Das Skript liegt in: {script_dir}")
    except PermissionError:
        print("Fehler: Du hast keine Berechtigung, diese Datei zu lesen.")
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
    finally:
        print("--------------------------------")
    
    print(f"\nErstelle KVM {vm['safe_name']} ")
    try:
        

        # Anwendung:
        if is_vm_installed(vm['safe_name']):
            print(f"{UI.YELLOW}[ INFO ] VM '{vm['safe_name']}' ist bereits im System registriert.{UI.RESET}")
            choice = input(f"Möchtest du sie [ü]berschreiben oder [b]ehalten? (ü/b): {UI.RESET}").lower()

            if choice == 'ü':
                print(f"Lösche alte VM '{vm['safe_name']}'...")
                # Erst stoppen (erzwingen), dann löschen inklusive Speicher
                subprocess.run(
                    ["virsh", "destroy", 
                    vm['safe_name']],
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL, 
                )
                subprocess.run(
                    ["virsh", "undefine", 
                    vm['safe_name'], "--remove-all-storage"], 
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True)
            else:
                print(f"{UI.GREEN}Behalte bestehende VM. Installation übersprungen.{UI.RESET}")
                
                #return # Funktion beenden, nichts weiter tun


        final_cmd_string = f" ".join(vm['generated_cmd'])
      #  print(f"\033[96m{final_cmd_string}\033[0m")
        result = subprocess.run(vm['generated_cmd'], check=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"{UI.GREEN}Erfolg: {vm['safe_name']} ist bereit.{UI.RESET}")
    except subprocess.CalledProcessError as e:
        print(f"{UI.RED}DER KVM-BEFEHL SCHLUG FEHL!{UI.RESET}")
        print(f"Meldung: {e.stderr.strip()}")
    except Exception as e:
        print(f"{UI.RED}Ein unerwarteter Fehler ist aufgetreten: {e}{UI.RESET}")





