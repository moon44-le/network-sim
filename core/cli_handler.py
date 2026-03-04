from lib.tools import UI

class CLIHandler:
    def __init__(self, deploy_manager, vm_manager):
        UI.setup_shell_history(UI.history_file)
        self.deployer = deploy_manager
        self.vm_mgr = vm_manager
        self.syntax_help = (
            "  start <slug|all>    - Startet die VM(s)\n"
            "  destroy <slug|all>  - Stoppt die VM(s) sofort\n"
            "  undefine <slug|all> - Löscht die VM(s) kaskadiert\n"
            "  create <slug>       - Erstellt VM aus YAML-Config\n"
            "  list                - Zeigt den Statusbericht\n"
            "  --help              - Zeigt diese Hilfe an\n"
            "  exit                - Beendet das Programm"
        )

    def show_terminal_overview(self):
        # Die Logik zum Zeichnen der Tabelle
        report = self.vm_mgr.get_all_statuses() # Logik kommt vom VMManager
        print("\n" + "="*65)
        print(f"{'DOMAIN':<12} | {'VM':<12} | {'SERVICE':<20} | {'SLUG'}")
        print("-"*65)
        # ... Schleife für die Anzeige ...
        print("="*65 + "\n")

    def start_shell(self):
        
        """Die Endlosschleife, die wir aus der main ausgelagert haben."""
        while True:
            cmd_input = input("KVM Manager: ").strip().lower()
            if cmd_input in ["exit", "quit", "q"]:
                break
            
            # Hier rufst du die internen Methoden auf
            self.process_command(cmd_input)

    def process_command(self, cmd_input):
        parts = cmd_input.split()
        action = parts[0]
        target = parts[1] if len(parts) > 1 else None

        if not target:
            print(f"\n{self.syntax_help}\n")
        pass