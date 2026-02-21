import subprocess
import os

class UI:
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    RESET = "\033[0m"

    @staticmethod
    def clear():
        command = "cls" if os.name == "nt" else "clear"
        subprocess.run([command])

    @staticmethod
    def header(text):
        print(f"{UI.GREEN}=== {text} ==={UI.RESET}\n")

class KVM:
    @staticmethod
    def is_installed(vm_name):
        # --name gibt nur die Namen zurück, --all zeigt auch ausgeschaltete VMs
        check_cmd = ["virsh", "list", "--all", "--name"]
        result = subprocess.run(check_cmd, capture_output=True, text=True)
        installed_vms = result.stdout.splitlines()
        return vm_name in [name.strip() for name in installed_vms]

    @staticmethod
    def delete(vm_name):
     #   subprocess.run(["virsh", "destroy", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
     #   subprocess.run(["virsh", "undefine", name, "--remove-all-storage"], check=True)
        subprocess.run(
            ["virsh", "destroy", vm_name],
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL)
        subprocess.run(
            ["virsh", "undefine", vm_name, "--remove-all-storage"], 
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True)