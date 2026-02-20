import yaml
import shlex
import subprocess # Für lokale Tests, später durch SSH (paramiko) ersetzbar

from pathlib import Path

def create_kvm_command(config_path):
    # 1. YAML Datei laden
    with open(config_path, 'r') as file:
        data = yaml.safe_load(file)
    
    # 2. Werte aus dem Dictionary extrahieren
    vm = data['vm_metadata']
    
    # 3. Werte sicher für die Shell maskieren (shlex)
    # Das verhindert, dass Namen wie "Web Server" den Befehl zerbrechen
    safe_name = shlex.quote(vm['name'])
    safe_ram = shlex.quote(str(vm['ram_mb']))
    safe_vcpus = shlex.quote(str(vm['vcpus']))
    safe_disk = shlex.quote(str(vm['disk_gb']))
    
    # 4. Den finalen Befehl zusammenbauen (Der "Stream-String")
    # Wir nutzen virt-install als Beispiel-Tool auf dem Zielserver
    command = (
        f"virt-install "
        f"--name {safe_name} "
        f"--memory {safe_ram} "
        f"--vcpus {safe_vcpus} "
        f"--disk size={safe_disk} "
        f"--os-variant {vm['os_type']} "
        f"--graphics none "
        f"--import --dry-run" # --dry-run testet nur, ohne echt zu installieren
    )
    
    return command

# --- HAUPTPROGRAMM ---
if __name__ == "__main__":
    config_file = './setup/vm_config.yaml'
    
    print(f"--- Lade Konfiguration aus {config_file} ---")
    try:
        final_cmd = create_kvm_command(config_file)
    except FileNotFoundError:
    # Dieser Teil wird nur ausgeführt, wenn die Datei fehlt
        current_dir = Path.cwd()
        print(f"Fehler: Die Datei '{config_file}' wurde nicht gefunden.")
        print(f"Du befindest dich gerade in: {current_dir}")
        # Falls du wissen willst, wo die Skript-Datei selbst liegt:
        script_dir = Path(__file__).parent
        print(f"Das Skript liegt in: {script_dir}")
    except PermissionError:
        # Falls die Datei da ist, du aber keine Leserechte hast
        print("Fehler: Du hast keine Berechtigung, diese Datei zu lesen.")
    except Exception as e:
        # Ein 'Fangnetz' für alle anderen unerwarteten Fehler
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
    finally:
        # Dieser Teil wird IMMER ausgeführt, egal ob ein Fehler auftrat oder nicht
        print("--------------------------------")

        print("\nFolgender Befehl würde an den Server gestreamt werden:")
        print(f"\033[96m{final_cmd}\033[0m") # In Cyan ausgegeben für bessere Lesbarkeit
    
    # Hier käme später deine SSH-Logik (z.B. mit Paramiko)
    # ssh.exec_command(final_cmd)
