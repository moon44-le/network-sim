from .assets import ResourceManager
from .package_manager import PackageManager
# Wir importieren unsere eigenen Exceptions für das zentrale Error-Handling
from .exceptions import ProvisioningError, ConnectionError

class DeployManager:
    def __init__(self, config_dict):
        self.config = config_dict
        # Der DeployManager hält Instanzen der Spezialisten
        self.resource_mgr = ResourceManager()
        self.package_mgr = PackageManager()

    def deploy_all(self):
        """Iteriert über alle Geräte in der YAML."""
        devices = self.config.get('devices', {})
        for name, data in devices.items():
            try:
                self.deploy_device(name, data)
            except ProvisioningError as e:
                # Hier greift unser zentrales Error-Handling:
                # Wir stoppen bei einem Fehler, damit kein halbes Netzwerk entsteht
                print(f"❌ Abbruch bei Gerät '{name}': {e}")
                raise

    def deploy_device(self, name, data):
        """Führt die Schritte für ein einzelnes Gerät aus."""
        ip = data.get('ip')
        print(f"--- 🚀 Starte Deployment: {name} ({ip}) ---")

        # 1. Schritt: Pakete & Ressourcen aus der YAML verarbeiten
        for item in data.get('provisioning', []):
            pkg_name = item.get('package')
            
            # Der ResourceManager sucht lokal oder gibt "REMOTE" zurück
            resource = self.resource_mgr.get_resource(pkg_name)
            
            # Der PackageManager führt die Installation aus (Local-First Logik)
            self.package_mgr.install(ip, pkg_name, resource)

            # 2. Schritt: Optionale Post-Commands (z.B. NAT aktivieren)
            if 'post_cmd' in item:
                self.package_mgr.execute_custom(ip, item['post_cmd'])

        print(f"--- ✅ {name} ist bereit! ---")