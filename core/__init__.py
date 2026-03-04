# core/__init__.py

from .config_manager import ConfigManager
# from .deploy_manager import DeployManager
import core.hypervisor  as Hypervisor   # Er repräsentiert die Virtualisierungs-Schicht.
import core.library      as Library     # Er tut genau das: Installieren
import core.fabric      as Fabric      # Die Infrastruktur.
# import orchestrator # Er ist die Schaltzentrale, die alles zusammenführt.