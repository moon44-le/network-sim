import yaml

def load_network_config(filepath="./setup/vm_config.yaml"):

    try:
        with open(filepath, 'r') as file:
            # yaml.safe_load konvertiert YAML direkt in Python-Listen/Dicts
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Fehler: Die Datei {filepath} wurde nicht gefunden.")
        return []

# Wir laden die Daten direkt beim Import der Config
NET_SIM_VMS = load_network_config()