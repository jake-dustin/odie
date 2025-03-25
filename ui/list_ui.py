# list_ui.py
from abc import abstractmethod

from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel

from console_instance import console
from ui import Action


def format_action(action):
    if action.is_enabled():
        return f"[bold green][{action.key}][/bold green] {action.label}"
    else:
        return f"[dim][{action.key}] {action.label}[/dim]"


class ListUI:
    @property
    @abstractmethod
    def _name(self):
        """The name of a list module. Must be implemented."""
        return None

    def __init__(self, title, items):
        """
        Args:
            title (str): The title of the list UI.
            items (list[dict]): The list of items to display.
        """
        self.title = title
        self.items = items

    @property
    def default_actions(self):
        return [
            Action("H", "Home", self.home),
            Action("Q", "Quit", self.quit)
        ]

    def get_enabled_actions(self):
        """Return only actions whose conditions are met."""
        return [action for action in self.default_actions if action.is_enabled()]

    def display_table(self, items=None):
        if items is None:
            items = self.items

        table = Table(title=self.title)
        table.add_column("Index", justify="right", style="cyan")
        table.add_column("Name", style="magenta")
        for index, item in enumerate(items, start=1):
            item_dict = dict(item)
            table.add_row(str(index), item_dict.get("name", "N/A"))
        console.print(table)

    def prompt_action(self):
        enabled_actions = self.get_enabled_actions()
        choice = Prompt.ask("Select an action", default="Q")
        # Execute the function associated with the selected action.
        for action in enabled_actions:
            if action.key == choice:
                result = action.func()
                if action.key == "Q":
                    return result
                return result if result is not None else self
        return self

    def prompt_for_item(self, action_label):
        console.print(f"\n[bold yellow]Select an item to {action_label.lower()}[/bold yellow]\n")
        self.display_table()
        choice = Prompt.ask(
            f"Select an item to {action_label.lower()}",
            choices=[str(i) for i in range(1, len(self.items) + 1)]
        )
        return int(choice) - 1

    def display_actions(self):
        """
        Overrides the default display_actions to show all actions,
        but formats enabled actions differently from disabled ones.
        """
        formatted = "\n".join(format_action(action) for action in self.default_actions)
        panel = Panel(formatted, title="Actions", expand=False)
        console.print(panel)

    def home(self):
        from ui.dashboard_list_ui import DashboardUI
        console.print(f"[bold blue]Going to home dashboard...[/bold blue]")
        return DashboardUI()

    def quit(self):
        """Handles quitting the migrations UI."""
        console.print(f"[bold red]Exiting {self._name}[/bold red]")
        return None