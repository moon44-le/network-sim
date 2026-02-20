import shlex

vm_name = "Mein Web Server"  # Leerzeichen sind riskant in Shell-Commands
safe_name = shlex.quote(vm_name)

# Das resultiert in: 'Mein\ Web\ Server' - sicher für die Shell!
command = f"virt-install --name {safe_name} ..."
