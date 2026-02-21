import yaml

def load_network_config(filepath="./setup/vm_config.yaml"):

    try:
        with open(filepath, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"FileNotFoundError: {filepath}")
        return []
    except PermissionError:
        print(f"PermissionError: {filepath}")
        return []
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")


# Wir laden die Daten direkt beim Import der Config
NET_SIM_VMS = load_network_config()