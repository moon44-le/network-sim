# KVM Network Simulator

Ein modularer, Python-basierter Netzwerksimulator zur automatisierten Verwaltung von KVM-Umgebungen. Dieses Tool schließt die Lücke zwischen Infrastruktur-Definition (YAML), Hypervisor-Steuerung (Libvirt/Virsh) und Software-Konfiguration (Ansible).

## 1. Vision & Zweck
Das Ziel dieses Projekts ist es, komplexe Netzwerk-Topologien (Router, Gateways, Server) deklarativ zu beschreiben und auf Knopfdruck bereitzustellen. 
* **Soll-Zustand:** Definiert in einer zentralen `config.yaml`.
* **Ist-Zustand:** Live-Abgleich mit dem KVM-Host via `virsh`.
* **Automatisierung:** Automatisches Deployment und Provisionierung.

## 2. Architektur & Module

Das Projekt folgt dem Prinzip der **Separation of Concerns**, um maximale Kontrolle und Erweiterbarkeit zu gewährleisten:

* **`main.py`**: Einstiegspunkt; lädt die Konfiguration und initialisiert das System.
* **`core/cli_handler.py`**: Interaktive Shell-Schnittstelle. Ermöglicht das Management des Labs in Echtzeit (Cockpit-Funktion).
* **`core/orchestrator.py`**: Das "Gehirn". Vergleicht die YAML-Vorgaben mit der System-Realität (**Matching**) und koordiniert die Modul-Aufrufe.
* **`core/hypervisor.py`**: Schnittstelle zu `virsh` und `virt-install`. Verantwortlich für das Lifecycle-Management der VMs (Hardware-Ebene).
* **`core/provisioner.py`**: Schnittstelle zu **Ansible**. Konfiguriert die Software innerhalb der VMs, sobald diese via SSH erreichbar sind.
* **`core/system.py`**: Zentrales Error-Handling und sichere Ausführung von Shell-Befehlen (`safe_execute`).

## 3. Workflow & Technologien

### Infrastruktur mit `virsh`
Die Verwaltung der virtuellen Maschinen erfolgt über die Libvirt-Toolchain. 
- **Matching:** Der Orchestrator prüft den Status (`RUNNING`, `SHUT OFF`, `NOT DEFINED`) direkt über `virsh`.
- **Idempotenz:** Befehle werden nur ausgeführt, wenn der aktuelle Zustand vom Soll-Zustand abweicht (z.B. wird eine bereits laufende VM nicht erneut gestartet).

### Konfiguration mit Ansible
Sobald die Infrastruktur bereitsteht, übernimmt Ansible die softwareseitige Einrichtung:
- Installation von Netzwerk-Tools.
- Konfiguration von Routing-Tabellen und IP-Forwarding.
- Setup von spezifischen Diensten je nach Rolle der VM.

## 4. Bedienung (CLI-Befehle)
Innerhalb des `CLIHandler` stehen folgende Kernbefehle zur Verfügung:

| Befehl | Beschreibung |
| :--- | :--- |
| `list` | Zeigt den Live-Status aller in der YAML definierten VMs an. |
| `create <slug>` | Registriert eine neue VM im Hypervisor, falls sie noch nicht existiert. |
| `start <slug>` | Startet eine vorhandene, aber ausgeschaltete VM. |
| `deploy` | Führt den kompletten Prozess (Matching -> Start -> Ansible) für das gesamte Lab aus. |
| `exit` | Beendet die interaktive Sitzung. |

---
*Status: In aktiver Entwicklung. Fokus auf robuste Matching-Logik und dynamische virsh-Parser.*