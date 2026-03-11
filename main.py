from core.orchestrator import Orchestrator
from core.cli_handler import CLIHandler
from core.exceptions import NetworkSimError

def main():
    #config = load_yaml("config.yaml")
    #engine = Orchestrator(config)

    # 1. Datei laden (Einmalig zentral)
    try:
        with open("./data/vm_config.yaml", "r") as f:
            raw_data = yaml.safe_load(f)
    except Exception as e:
        print(f"Fehler beim Laden der Config: {e}")
        return

    # 2. Orchestrator initialisieren (verarbeitet die Daten intern)
    orchestrator = Orchestrator(raw_data)

    # 3. CLI starten
    cli = CLIHandler(orchestrator)
    cli.start_shell()
        #engine.deploy_all()
        #print("[V] Deployment erfolgreich abgeschlossen!")
    
    #except NetworkSimError as e:
        # Hier fängst du ALLES ab, was in deinen Modulen schiefgeht
     #   print(f"\n[!!!] ABBRUCH des Deployments [!!!]")
      #  print(e)
        # Hier könntest du eine Cleanup-Funktion aufrufen