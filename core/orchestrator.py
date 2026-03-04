# core/orchestrator.py
import core

class Orchestrator:
    def __init__(self):
        # Der Orchestrator baut sich seine Werkzeuge selbst zusammen
        self.config  = ConfigLoader(config_path)
        self.assets  = Assets()
        self.network = Fabric()
        self.vms     = Hypervisor()
        self.install = Installer()

    def build_lab(self):
        """Hier fließt alles zusammen."""
        self.network.setup_bridges()
        for node in self.config.nodes:
            self.vms.start(node)
            self.install.apply(node, self.assets)