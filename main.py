from core.orchestrator import Orchestrator
from core.exceptions import NetworkSimError

def main():
    config = load_yaml("config.yaml")
    engine = Orchestrator(config)

    try:
        engine.deploy_all()
        print("[V] Deployment erfolgreich abgeschlossen!")
    
    except NetworkSimError as e:
        # Hier fängst du ALLES ab, was in deinen Modulen schiefgeht
        print(f"\n[!!!] ABBRUCH des Deployments [!!!]")
        print(e)
        # Hier könntest du eine Cleanup-Funktion aufrufen