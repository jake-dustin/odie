# main.py
#!/usr/bin/env python3
from console_instance import console  # Import the console from ui.py
from ui.migrations_list_ui import MigrationsListUI


def main_loop(starting_ui):
    current_ui = starting_ui
    while current_ui:
        console.clear()
        current_ui.display_table()
        current_ui.display_actions()
        current_ui = current_ui.prompt_action()

if __name__ == "__main__":
    # start with migrations UI
    main_loop(MigrationsListUI())