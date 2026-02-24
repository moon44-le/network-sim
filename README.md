# KVM

KVM (Kernel-based Virtual Machine) ist eine Open-Source-Virtualisierungstechnologie für Linux, die den Linux-Kernel in einen Hypervisor verwandelt. Sie ermöglicht es, mehrere isolierte virtuelle Maschinen (Gäste) mit fast nativer Geschwindigkeit direkt auf der Hardware des Host-Systems auszuführen.

## Funktionen

* Installieren der benötigten Pakete
* Setzen der Gruppenrechte "libvirt kvm"

### Benötigte Pakete für KVM-Virtualisierung

| Paket | Funktion | Warum du es brauchst |
| :--- | :--- | :--- |
| **`qemu-kvm`** | Emulator & Beschleuniger | **QEMU** emuliert die Hardware (Festplatten, Grafikkarten). **KVM** ist das Kernel-Modul, das dafür sorgt, dass die CPU-Befehle direkt auf der echten CPU laufen. Ohne das wäre die VM extrem langsam. |
| **`libvirt-daemon-system`** | Der Hintergrunddienst | Dies ist der "Manager", der im Hintergrund läuft. Er konfiguriert die VMs beim Start, verwaltet den Speicher und sorgt dafür, dass die VMs auch nach einem Neustart des Hosts korrekt behandelt werden. |
| **`libvirt-clients`** | Steuerungs-Tools | Enthält Befehlszeilen-Tools wie `virsh`. Damit kannst du VMs über das Terminal stoppen, starten oder bearbeiten, ohne eine grafische Oberfläche zu benötigen. |
| **`bridge-utils`** | Netzwerk-Brücken | Erlaubt es dir, virtuelle Netzwerkbrücken zu erstellen. Damit kann deine VM so tun, als wäre sie ein eigenständiges Gerät in deinem physischen Netzwerk (statt nur hinter einem NAT versteckt zu sein). |
| **`virt-manager`** | Die grafische Oberfläche | Wenn du nicht alles im Terminal tippen willst, ist dies das Fenster, in dem du "Neu", "Start" und "Konfigurieren" klicken kannst. Es ist das visuelle Kontrollzentrum. |
| **`wget`** | Download-Tool | Ein einfaches Werkzeug, um Dateien (wie ISO-Abbilder von Betriebssystemen) direkt über das Terminal aus dem Internet herunterzuladen. |
