#!/bin/bash#!/bin/bash

# Sorgt dafür, dass das Skript im eigenen Verzeichnis arbeitet
cd "$(dirname "$0")"

# 1. Installation der Pakete
echo ">>> Schritt 1: Installiere KVM & Management-Tools..."
sudo apt update
sudo apt install -y qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virt-manager wget

# 2. Gruppen-Check & User-Hinzufügung
GROUPS_NEEDED=("libvirt" "kvm")
RESTART_NEEDED=false

for GROUP in "${GROUPS_NEEDED[@]}"; do
    if ! id -nG "$USER" | grep -qw "$GROUP"; then
        echo ">>> Füge $USER zu $GROUP hinzu..."
        sudo usermod -aG "$GROUP" "$USER"
        RESTART_NEEDED=true
    fi
done

# 3. Der Self-Restart Trick für sofortige Gruppenrechte
if [ "$RESTART_NEEDED" = true ] && [ "$ENV_RESTARTED" != "true" ]; then
    echo ">>> Aktiviere Gruppenrechte und setze Automatisierung fort..."
    export ENV_RESTARTED=true
    exec sg libvirt "$0"
fi

# 4. Infrastruktur-Check
echo ">>> Schritt 2: Infrastruktur-Check..."
if virsh list --all > /dev/null 2>&1; then
    echo "    ERFOLG: KVM-Zugriff ist aktiv!"
else
    echo "    FEHLER: Kein Zugriff auf KVM. Bitte nach dem Skriptlauf einmal neu anmelden."
fi

# 5. ISO Download
ISO_DIR="$HOME/Downloads"
ISO_NAME="debian-12-netinst.iso"
# Aktueller Link für Debian 12
ISO_URL="https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-12.9.0-amd64-netinst.iso"

if [ ! -f "$ISO_DIR/$ISO_NAME" ]; then
    echo ">>> Schritt 3: Lade Debian ISO herunter..."
    wget -v -O "$ISO_DIR/$ISO_NAME" "$ISO_URL"
else
    echo ">>> Schritt 3: Debian ISO bereits vorhanden. Überspringe Download."
fi

echo "------------------------------------------------------"
echo "SETUP ABGESCHLOSSEN."
echo "Deine VM-Grundlage ist bereit."
echo "Ort des ISOs: $ISO_DIR/$ISO_NAME"
echo "------------------------------------------------------"

# Skript von überall ausführen
cd "$(dirname "$0")"

# 1. Installation der Pakete (muss mit sudo sein, braucht keine Gruppe)
echo "Schritt 1: Pakete installieren..."
sudo apt update
sudo apt install -y qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virt-manager

# 2. Gruppen-Check
GROUPS_NEEDED=("libvirt" "kvm")
RESTART_NEEDED=false

for GROUP in "${GROUPS_NEEDED[@]}"; do
    if ! id -nG "$USER" | grep -qw "$GROUP"; then
        echo "Füge $USER zu $GROUP hinzu..."
        sudo usermod -aG "$GROUP" "$USER"
        RESTART_NEEDED=true
    fi
done

# 3. Der Trick: Falls Gruppen neu waren, Skript in neuer Umgebung neu starten
if [ "$RESTART_NEEDED" = true ] && [ "$ENV_RESTARTED" != "true" ]; then
    echo "Aktiviere Gruppenrechte und setze Automatisierung fort..."
    export ENV_RESTARTED=true
    exec sg libvirt "$0"  # $0 ist der Pfad zum aktuellen Skript selbst
fi

# --- AB HIER GEHT DIE AUTOMATISIERUNG WEITER ---
echo "Schritt 2: Infrastruktur-Check..."
if virsh list --all > /dev/null 2>&1; then
    echo "ERFOLG: KVM-Zugriff ohne sudo möglich!"
else
    echo "FEHLER: Zugriff auf KVM verweigert."
    exit 1
fi

# 4. Beispiel für weiteren Schritt: Standard-Netzwerk starten
echo "Schritt 3: Virtuelles Standard-Netzwerk aktivieren..."
sudo virsh net-start default 2>/dev/null
sudo virsh net-autostart default

echo "------------------------------------------------------"
echo "VOLLSTÄNDIG ABGESCHLOSSEN: Dein System ist bereit für die VM."
echo "------------------------------------------------------"