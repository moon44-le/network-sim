import subprocess
from .exceptions import ProvisioningError, HypervisorError

def safe_execute(cmd_list, description, error_type="provisioning"):
    """
    Führt Befehle aus und wirft je nach Kontext die richtige Exception.
    """
    try:
        print(f"[*] {description}...")
        return subprocess.run(cmd_list, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        msg = (f"Fehler bei: {description}\n"
               f"Exit-Code: {e.returncode}\n"
               f"Details: {e.stderr.strip()}")
        
        if error_type == "hypervisor":
            raise HypervisorError(msg)
        raise ProvisioningError(msg)