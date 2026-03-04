from dataclasses import dataclass
from typing import List

@dataclass
class DeviceConfig:
    name: str
    ip: str
    role: str
    packages: List[str]
    
    def is_gateway(self):
        return self.role == "gateway"

class ConfigManager:
    def __init__(self, yaml_path):
        self.raw_data = self._load(yaml_path)
        self.devices = self._validate_and_convert()

    def _validate_and_convert(self):
        # Hier prüfst du: Sind IPs gültig? Fehlen Pflichtfelder?
        # Dann konvertierst du das Dictionary in eine Liste von DeviceConfig-Objekten
        devices = []
        for name, data in self.raw_data['devices'].items():
            devices.append(DeviceConfig(name=name, **data))
        return devices