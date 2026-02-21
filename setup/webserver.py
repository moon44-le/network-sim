from tools import UI, KVM
import config 

import os
import yaml
import shlex
import subprocess # Für lokale Tests, später durch SSH (paramiko) ersetzbar

from pathlib import Path

# config.NET_SIM_VMS

config_file = './setup/vm_config.yaml'
# Pfad zum ISO (entspricht deinem wget-Pfad)
ISO_PATH = os.path.expanduser("/var/lib/libvirt/boot//debian-12-netinst.iso")
def start_deployment():
    UI.clear()
    UI.header("Deployment startet")
    
   
    for vm in config.NET_SIM_VMS:
       # print(config.NET_SIM_VMS)
        print(vm['name'])
        # 1. Existiert sie schon?
        if KVM.is_installed(vm['name']):
            print(f"{UI.YELLOW}[ INFO ] VM '{vm['name']}' ist bereits im System registriert.{UI.RESET}")
            choice = input(f"Möchtest du sie [ü]berschreiben oder [b]ehalten? (ü/b): {UI.RESET}").lower()

            if choice == 'ü':
                print(f"Lösche alte VM '{vm['name']}'...")
                KVM.delete(vm['name'])
            else:
                print(f"{UI.GREEN}Behalte bestehende VM. Installation übersprungen.{UI.RESET}")  
                return 
            pass
        
        # 2. Erstellen
        success = KVM.create(vm, ISO_PATH)
        if success:
            print(f"VM {vm['name']} wurde erfolgreich angestoßen.")
            print(f"{UI.GREEN}Erfolg: {vm['name']} ist bereit.{UI.RESET}")


# --- HAUPTPROGRAMM ---
if __name__ == "__main__":
    
    
    try:
        start_deployment()
 
    except subprocess.CalledProcessError as e:
        print(f"{UI.RED}DER KVM-BEFEHL SCHLUG FEHL!{UI.RESET}")
        print(f"Meldung: {e.stderr.strip()}")
    except Exception as e:
        print(f"Exception in start_deployment: {e.stderr.strip()}")
    finally:
        print("--------------------------------")
    

  




