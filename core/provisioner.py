import socket
import time
from .system import safe_execute

def wait_for_ssh(ip, timeout=60):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((ip, 22), timeout=1):
                return True
        except:
            time.sleep(2)
    return False

def run_playbook(ip, playbook_name):
    # Pfad relativ zur main.py
    path = f"./ansible/playbooks/{playbook_name}"
    cmd = [
        "ansible-playbook", "-i", f"{ip},", path,
        "-u", "root", "--ssh-common-args='-o StrictHostKeyChecking=no'"
    ]
    return safe_execute(cmd, f"Ansible Playbook {playbook_name}")