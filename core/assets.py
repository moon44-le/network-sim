import os

class assets:
    def __init__(self, base_path="./local_assets"):
        self.base_path = base_path
        self.config_dir = os.path.join(base_path, "configs")
        self.package_dir = os.path.join(base_path, "packages")
        self.script_dir = os.path.join(base_path, "scripts")

    def get_resource(self, name):
        """
        Sucht nach einer Ressource und klassifiziert sie.
        Gibt ein Dictionary mit Pfad und Typ zurück.
        """
        # 1. Suche nach .deb Paketen
        deb_path = os.path.join(self.package_dir, f"{name}.deb")
        if os.path.exists(deb_path):
            return {"path": deb_path, "type": "PACKAGE", "action": "dpkg -i"}

        # 2. Suche nach Konfigurationen
        conf_path = os.path.join(self.config_dir, f"{name}.conf")
        if os.path.exists(conf_path):
            return {"path": conf_path, "type": "CONFIG", "action": "upload"}

        # 3. Suche nach Shell-Skripten
        sh_path = os.path.join(self.script_dir, f"{name}.sh")
        if os.path.exists(sh_path):
            return {"path": sh_path, "type": "SCRIPT", "action": "execute"}

        # Fallback: Nichts lokal gefunden
        return {"path": None, "type": "REMOTE", "action": "apt-get"}

# --- Integration in den Provisioner ---

def provision_item(target, item_name):
    res = resource_mgr.get_resource(item_name)
    
    if res["type"] == "PACKAGE":
        # Logik: Hochladen und mit dpkg installieren
        upload_and_install_local(target, res["path"])
    elif res["type"] == "REMOTE":
        # Logik: Über das Internet laden
        install_from_apt(target, item_name)
    elif res["type"] == "CONFIG":
        # Logik: Pfad auflösen (z.B. /etc/{name}/{name}.conf)
        upload_config(target, res["path"])