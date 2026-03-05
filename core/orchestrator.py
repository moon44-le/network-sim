from . import hypervisor, fabric, provisioner

class Orchestrator:
    def __init__(self, config_data):
        self.devices = config_data.get('devices', [])

    def deploy_all(self):
        # 1. Netzwerk vorbereiten (einmalig)
        fabric.setup_bridge("br0")

        for dev in self.devices:
            name = dev['hostname']
            ip = dev['ip']
            playbook = dev['ansible_playbook']

            # 2. VM starten
            hypervisor.start_vm(name, dev)

            # 3. Warten auf SSH
            if provisioner.wait_for_ssh(ip):
                # 4. Provisionieren mit Ansible
                provisioner.run_playbook(ip, playbook)
            else:
                print(f"[!] Überspringe {name} wegen Timeout.")