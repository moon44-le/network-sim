import subprocess

from lib.inventory import Inventory
# from lib.bridge import Bridge
from lib.kvm import KVM
from lib.tools import UI 
from lib.tools import GatewayManager
import core
import config




from core import Library, Bridge, Orchestrator, Hypervisor, Fabric

def main():
    # 1. Die Werkzeuge bereitstellen (Explizit!)
    lib    = Library()
    hv     = Hypervisor()
    net    = Fabric.Bridge()
    
    # 2. Den Orchestrator mit den Werkzeugen füttern
    # Er "besitzt" die Werkzeuge nicht magisch, du gibst sie ihm einfach
    engine = Orchestrator(config_path="vm_config.yaml", 
                          library=lib, 
                          hypervisor=hv, 
                          fabric=net)

    # 3. Startschuss
    try:
        engine.run()
    except Exception as e:
        print(f"Abbruch: {e}")

if __name__ == "__main__":
    main()
