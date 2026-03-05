import subprocess
import os

def exists(network_name="br-intern"):
        """Prüft, ob das Netzwerk in Libvirt definiert ist."""
        cmd = ["sudo", "virsh", "net-list", "--all", "--name"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        networks = [n.strip() for n in result.stdout.splitlines()]
        return network_name in networks

def stop(network_name="br-intern"):
        """Stoppt das Netzwerk (entspricht 'Link down'), löscht es aber nicht."""
        if not Bridge.is_running(network_name):
            print(f"[*] Bridge '{network_name}' ist bereits gestoppt.")
            return True
        
        print(f"[*] Stoppe Bridge '{network_name}'...")
        cmd = ["sudo", "virsh", "net-destroy", network_name]
        return subprocess.run(cmd, capture_output=True).returncode == 0

def delete(network_name="br-intern"):
        """
        Löscht die Bridge komplett aus der Libvirt-Konfiguration.
        Stoppt sie vorher, falls sie noch läuft.
        """
        if not Bridge.exists(network_name):
            print(f"[!] Abbruch: Bridge '{network_name}' existiert nicht.")
            return False

        # Erst stoppen (destroy), dann Definition entfernen (undefine)
        Bridge.stop(network_name)
        
        print(f"[*] Lösche Definition von Bridge '{network_name}'...")
        cmd = ["sudo", "virsh", "net-undefine", network_name]
        success = subprocess.run(cmd, capture_output=True).returncode == 0
        if success:
            print(f"[+] Bridge '{network_name}' erfolgreich entfernt.")
        return success

def is_running(network_name="br-intern"):
        """Prüft, ob das Netzwerk aktiv ist (Status: active)."""
        cmd = ["sudo", "virsh", "net-list", "--name"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return network_name in [n.strip() for n in result.stdout.splitlines()]
    

def create_isolated(network_name="br-intern"):
        """
        Erstellt ein isoliertes virtuelles Netzwerk in Libvirt.
        In PHP wäre dies vergleichbar mit der Initialisierung eines Netzwerk-Objekts.
        """
        # 1. Prüfen, ob die Bridge bereits existiert
        if Bridge.exists(network_name):
            if not Bridge.is_running(network_name):
                print(f"[*] Bridge '{network_name}' existiert, ist aber inaktiv. Starte...")
                subprocess.run(["sudo", "virsh", "net-start", network_name], check=True)
            else:
                print(f"[*] Bridge '{network_name}' ist bereits aktiv.")
            return True

        # 2. XML-Definition für das isolierte Netzwerk
        # Dies ist der Industriestandard für Libvirt-Netzwerke
        network_xml = f"""
        <network>
          <name>{network_name}</name>
          <bridge name='{network_name}' stp='on' delay='0'/>
        </network>
        """
        
        xml_path = f"/tmp/{network_name}.xml"
        
        try:
            # XML schreiben
            with open(xml_path, "w") as f:
                f.write(network_xml)

            # Bei Libvirt definieren, starten und Autostart setzen
            subprocess.run(["sudo", "virsh", "net-define", xml_path], check=True)
            subprocess.run(["sudo", "virsh", "net-start", network_name], check=True)
            subprocess.run(["sudo", "virsh", "net-autostart", network_name], check=True)
            
            print(f"[+] Isolierte Bridge '{network_name}' erfolgreich erstellt.")
            os.remove(xml_path)
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"[-] Fehler beim Erstellen der Bridge: {e}")
            return False