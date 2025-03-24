# dashboard_ui.py
from ui.list_ui import ListUI
from ui.action import Action
from ui.migrations_list_ui import MigrationsListUI
from ui.clients_list_ui import ClientsListUI
from ui.sites_list_ui import SitesListUI
from console_instance import console

class DashboardUI(ListUI):
    @property
    def _name(self):
        return "Dashboard"

    def __init__(self):
        # The dashboard items are just labels for menu options.
        items = [
            {"name": "Go To Migrations"},
            {"name": "Go To Clients"},
            {"name": "Go To Sites"},
            {"name": "Quit Application"}
        ]
        super().__init__("Dashboard", items)

    @property
    def default_actions(self):
        # Each action returns a new UI instance, except Quit which returns None.
        return [
            Action("1", "Migrations", self.goto_migrations),
            Action("2", "Clients", self.goto_clients),
            Action("3", "Sites", self.goto_sites),
            Action("Q", "Quit", self.quit)
        ]

    def goto_migrations(self):
        console.print("[bold blue]Loading Migrations UI...[/bold blue]")
        return MigrationsListUI()

    def goto_clients(self):
        console.print("[bold blue]Loading Clients UI...[/bold blue]")
        return ClientsListUI()

    def goto_sites(self):
        console.print("[bold blue]Loading Sites UI...[/bold blue]")
        return SitesListUI()

    def quit(self):
        console.print("[bold red]Exiting application...[/bold red]")
        return None