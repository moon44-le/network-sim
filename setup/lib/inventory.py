import subprocess
from lib.tools import UI

class Inventory:

    @staticmethod
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

    @staticmethod
    def get_status_report(yaml_vms):
        host_vms = Inventory.get_all_host_vms() # Jetzt ein Dict {Name: State}
        report = []

        # 1. YAML-VMs abgleichen
        for vm in yaml_vms:
            slug = vm.get('hostname', vm['name']).lower().replace(" ", "_")
            
            if slug in host_vms:
                state = host_vms[slug]
                report.append({
                    "name": vm['name'],
                    "slug": slug,
                    "status": "INSTALLED",
                    "state": state.upper(),
                    "color": UI.GREEN if state == "running" else "\033[36m" # Grün wenn läuft, Cyan wenn aus
                })
            else:
                report.append({
                    "name": vm['name'],
                    "slug": slug,
                    "status": "MISSING",
                    "state": "NOT FOUND",
                    "color": UI.WHITE
                })
        
        # 2. Unbekannte VMs (Schatten-IT)
        for h_name, h_state in host_vms.items():
            if h_name not in [vm.get('hostname', vm['name']).lower().replace(" ", "_") for vm in yaml_vms]:
                report.append({
                    "name": "Unbekannt",
                    "slug": h_name,
                    "status": "UNKNOWN",
                    "state": h_state.upper(),
                    "color": UI.YELLOW 
                })

        return report