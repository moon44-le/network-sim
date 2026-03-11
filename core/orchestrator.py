from . import hypervisor, provisioner, fabric

class Orchestrator:
    
    def __init__(self, raw_config_data):
        """
        Der Orchestrator erhält die bereits geladenen YAML-Daten.
        Hier findet die Aufbereitung statt (deine alte Logik).
        """
        self.devices = self._parse_config(raw_config_data)

    def _parse_config(self, data):
        """
        Deine alte Logik aus der config.py:
        Iteriert über Kategorien und fügt Rollen hinzu.
        """
        vms_dict = data.get('vms', {})
        all_vms = []

        for category, vm_list in vms_dict.items():
            for vm in vm_list:
                # Rolle setzen (z.B. gateways -> gateway)
                vm['role'] = category.rstrip('s')
                all_vms.append(vm)
        
        return all_vms





    def get_status_report(self):
        self.current_vm_status = hypervisor.get_status_report()
    

    def deploy_all(self):
        # 1. Infrastruktur (einmalig)
        fabric.setup_bridge("br0")

        # 2. Iteration über alle Devices in der YAML
        for dev in self.devices:
            hostname = dev.get('hostname')
            ip = dev.get('ip')
            playbook = dev.get('ansible_playbook')

            # Hardware-Start
            hypervisor.start_vm(hostname, dev)

            # Software-Provisionierung
            if provisioner.wait_for_ssh(ip):
                provisioner.run_playbook(ip, playbook)
            else:
                print(f"[!] {hostname} nicht erreichbar. Überspringe...")