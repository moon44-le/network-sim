from core.orchestrator import Orchestrator
from core.cli_handler import CLIHandler
import yaml

def main():

    try:
        with open("./vm_config.yaml", "r") as f:
            raw_data = yaml.safe_load(f)
    except Exception as e:
        print(f"Fehler beim Laden der Config: {e}")
        return

    # 2. Orchestrator initialisieren (verarbeitet die Daten intern)
    orchestrator = Orchestrator(raw_data)

    # 3. CLI starten
    cli = CLIHandler(orchestrator)
    cli.start_shell()

main()