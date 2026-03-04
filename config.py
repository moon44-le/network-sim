import yaml

def load_network_config(filepath="./data/vm_config.yaml"):

    try:
        with open(filepath, 'r') as file:

            data = yaml.safe_load(file)
            #  return data.get('vms', [])

        vms_dict = data.get('vms', {})
        all_vms = []

        # Wir iterieren über die Kategorien (gateways, clients, servers...)
        for category, vm_list in vms_dict.items():
            for vm in vm_list:
                # Wir fügen die Rolle/Kategorie direkt zum VM-Objekt hinzu
                # In PHP: $vm['role'] = $category;
                vm['role'] = category.rstrip('s') # Entfernt das 's' von 'gateways' -> 'gateway'                    
                all_vms.append(vm)            
        return all_vms

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