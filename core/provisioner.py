from .system import safe_execute
from .exceptions import ProvisioningError

def run_playbook(ip, playbook_name):
    """
    Startet Ansible. Wenn Ansible fehlschlägt, wirft safe_execute
    automatisch einen ProvisioningError.
    """
    path = f"./ansible/playbooks/{playbook_name}"
    cmd = [
        "ansible-playbook", 
        "-i", f"{ip},", 
        path,
        "-u", "root", 
        "--ssh-common-args='-o StrictHostKeyChecking=no'"
    ]
    
    # Hier wird safe_execute genutzt
    return safe_execute(cmd, f"Ansible Playbook {playbook_name} für {ip}")