import subprocess
from .exceptions import ProvisioningError

class SystemRunner:
    """Verantwortlich für alle lokalen Systembefehle auf dem Host-Rechner."""

    @staticmethod
    def run_local(cmd, description="Systembefehl"):
        """Führt einen Befehl lokal aus und fängt Fehler ab."""
        try:
            # Wir nutzen wieder unsere bewährte Logik
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=True,
                shell=isinstance(cmd, str) # Erlaubt sowohl Listen als auch Strings
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise ProvisioningError(
                f"Lokaler Fehler bei: {description}\n"
                f"Output: {e.stderr if e.stderr else e.stdout}"
            )

    @staticmethod
    def check_dependency(tool_name):
        """Prüft, ob ein benötigtes Tool (z.B. qemu, ssh) installiert ist."""
        try:
            subprocess.run(["which", tool_name], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False