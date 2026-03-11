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
        """Gleicht die YAML-Devices mit den echten Host-VMs ab."""
        host_vms = hypervisor.get_all_host_vms()
        report = []

        for dev in self.devices:
            slug = dev.get('slug') # oder 'hostname', je nach deiner YAML
            status = host_vms.get(slug, "NOT DEFINED")
            
            report.append({
                "slug": slug,
                "role": dev.get('role'),
                "ip": dev.get('ip', 'N/A'),
                "status": status.upper()
            })
        return report
    

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

    def remove_vm(self, slug):
        """Hier landet deine kaskadierte Logik von KVM.undefine."""
        states = hypervisor.get_all_host_vms()
        if slug not in states:
            return

        if "running" in states[slug].lower():
            print(f"[*] {slug} läuft noch. Stoppe erst...")
            hypervisor.stop_node(slug) # via virsh destroy

        print(f"[*] Lösche {slug} permanent...")
        hypervisor.undefine_node(slug)

    def deploy_node(self, vm_config):
        """Hier landet die Logik von KVM.create."""
        slug = vm_config['slug']
        
        # 1. Schritt: Disk vorbereiten (Delegation an Hypervisor)
        hypervisor.copy_base_image(vm_config['base_image'], f"/path/to/{slug}.qcow2")
        
        # 2. Schritt: Cloud-Init (Delegation an Hypervisor)
        # ...
        
        # 3. Schritt: Registrieren
        hypervisor.virt_install(vm_config)