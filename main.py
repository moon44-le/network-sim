import subprocess

from lib.inventory import Inventory
from lib.bridge import Bridge
from lib.kvm import KVM
from lib.tools import UI
import config


def show_terminal_overview():
    # 1. Daten holen (die Liste von Dictionaries)
    report = Inventory.get_status_report(config.NET_SIM_VMS)
    
    print("\n" + "="*65)
    print(f"{'STATUS':<12} | {'STATE':<12} | {'VM NAME':<20} | {'SLUG'}")
    print("-"*65)
    
    for vm in report:
        # Wir extrahieren die Werte aus dem Dictionary
        status = vm['status']
        state  = vm['state']
        name   = vm['name']
        slug   = vm['slug']
        color  = vm.get('color', '')
        reset  = "\033[0m"
        
        # :<12 sorgt dafür, dass der Text linksbündig auf 12 Zeichen aufgefüllt wird
        print(f"{color}{status:<12}{reset} | {state:<12} | {name:<20} | {slug}")
        
    print("="*65 + "\n")


def start_kvm_shell():

    syntax_help = (
        f"SYNTAX"
        f"  start <slug|all>    - Startet die VM(s)\n"
        f"  destroy <slug|all>  - Stoppt die VM(s) sofort\n"
        f"  undefine <slug|all> - Löscht die VM(s) kaskadiert\n"
        f"  create <slug>       - Erstellt VM aus YAML-Config\n"
        f"  list                - Zeigt den Statusbericht\n"
        f"  --help              - Zeigt diese Hilfe an\n"
        f"  exit                - Beendet das Programm"
    )

    UI.setup_shell_history(UI.history_file)

    while True:
  
        cmd_input = input(f"KVM Manager:").strip().lower()
        
        if not cmd_input:
            continue
        
        if cmd_input in ["exit", "quit", "q"]:
            break

        if cmd_input == "list":
           show_terminal_overview()
           continue

        if cmd_input == "--help":
            print(f"\n{syntax_help}\n")
            continue

        # 3. Syntax zerlegen: "start slug01" -> ["start", "slug01"]
        parts = cmd_input.split()
        action = parts[0]
        target = parts[1] if len(parts) > 1 else None

        if not target:
            print("[!] Syntax-Fehler: Bitte 'aktion slug' oder 'aktion all' eingeben.")
            continue

        # 4. Logik-Verteilung
        # Wir sammeln alle betroffenen Slugs in einer Liste
        report = Inventory.get_status_report(config.NET_SIM_VMS)
        
        if target == "all":
            # Alle Slugs nehmen, die entweder in der YAML stehen oder Geister sind
            targets = [vm['slug'] for vm in report]
        else:
            targets = [target]

        # 5. Ausführung
        for slug in targets:
            if action == "start":
                KVM.start(slug)
            elif action == "destroy":
                KVM.destroy(slug)
            elif action == "undefine":
                # Nutzt deine bereits kaskadierte Logik (inkl. destroy)
                KVM.undefine(slug)
            elif action == "create" and target != "all":
                # Für create brauchen wir die Config aus der YAML
                vm_cfg = next((vm for vm in config.NET_SIM_VMS if vm.get('hostname') == slug), None)
                vm_iso_path = "fdfd"

                if vm_cfg:
                    KVM.create(vm_cfg)
                else:
                    print(f"[!] Keine Konfiguration für '{slug}' in YAML gefunden.")
            else:
                print(f"[!] Unbekannte Aktion oder ungültige Kombination: {action}")
                break

if __name__ == "__main__":
    try:
      #  Bridge.create_isolated("br-intern")
        show_terminal_overview()
        start_kvm_shell()

    except subprocess.CalledProcessError as e:
        print(f"{UI.RED}DER KVM-BEFEHL SCHLUG FEHL!{UI.RESET}")
        print(f"CalledProcessError: {e.stderr.strip()}")
    except Exception as e:
        print(f"Exception: {e}")
    finally:
        print("--------------------------------")