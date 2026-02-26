#!/bin/sh

# 1. Verzeichnis wechseln (POSIX-konform)
cd "$(dirname "$0")"

# 2. Installation (Paketmanager sind OS-spezifisch, aber der Aufruf ist sh-sicher)
echo ">>> Schritt 1: Installation..."
sudo apt-get update

# System-Abhängigkeiten installieren
# WICHTIG: libvirt-python ist über apt oft stabiler als über pip
sudo apt-get install -y \
    qemu-kvm \
    libvirt-daemon-system \
    libvirt-clients \
    bridge-utils \
    virt-manager \
    wget \
    python3-pip \
    python3-yaml \
    python3-libvirt \
    cloud-image-utils

echo "Abhängigkeiten sind nun über das System installiert."

# 3. Gruppen-Check (Ohne Arrays!)
# Wir nutzen eine einfache Schleife über einen String
needed_groups="libvirt kvm"
restart_needed=0

for group in $needed_groups; do
    # Prüfen, ob User in Gruppe ist (id -G gibt IDs aus, grep sucht die Gruppen-ID)
    if ! id -nG "$USER" | grep -q "$group"; then
        echo ">>> Füge $USER zu $group hinzu..."
        sudo usermod -aG "$group" "$USER"
        restart_needed=1
    fi
done

# 4. Der Self-Restart (POSIX-kompatibel und sicher gegen "not found")
if [ "$restart_needed" -eq 1 ] && [ "$ENV_RESTARTED" != "true" ]; then
    echo ">>> Aktiviere Gruppenrechte..."
    ENV_RESTARTED="true"
    export ENV_RESTARTED
    # WICHTIG: Wir rufen 'sh' explizit auf und geben das Skript ($0) als Argument mit
    exec sg libvirt "sh $0"
fi

#5. ISO Download
#iso_dir="/var/lib/libvirt/boot/"
#iso_name="debian-12-netinst.iso"
#iso_url="https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-13.3.0-amd64-netinst.iso"
#echo -f "$iso_url"
#if [ ! -f"$iso_dir/$iso_name" ]; then
#    echo ">>> Schritt 3: Download..."
#    wget -O "$iso_dir/$iso_name" "$iso_url"
#fi
#echo "--- Fertig (POSIX Modus) ---"