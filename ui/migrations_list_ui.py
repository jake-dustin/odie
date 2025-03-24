from pathlib import Path

from rich.table import Table

from console_instance import console
from database import MigrationDAO
from helpers.validators import non_empty, validate_and_create_directory
from ui.action import Action
from ui.crud_mixin import CRUDMixin
from ui.paginated_list_ui import PaginatedListUI


class MigrationsListUI(CRUDMixin, PaginatedListUI):
    """UI for managing migrations."""
    MIGRATION_FIELD_DEFS = {
        "name": {
            "label": "Migration Name",
            "validator": non_empty,
        },
        "old_root": {
            "label": "Old Root Path",
            "validator": validate_and_create_directory,
            "default": str(Path.cwd()),
            "is_path": True,
        },
        "new_root": {
            "label": "New Root Path",
            "validator": validate_and_create_directory,
            "default": str(Path.cwd()),
            "is_path": True,
        },
    }

    def __init__(self, page=1):
        # Get the migrations from the DAO.
        self.items = MigrationDAO.get_all()
        super().__init__("Migrations", self.items, page)

    @property
    def default_actions(self):
        migration_actions = [
            Action("A", "Activate Migration", self.activate_migration, condition=self.is_item_modification_enabled),
            Action("C", "Create Migration", self.create_item),
            Action("E", "Edit Migration", self.edit_item, condition=self.is_item_modification_enabled),
            Action("D", "Delete Migration", self.delete_item, condition=self.is_item_modification_enabled),
        ]
        return migration_actions + super().default_actions

    @property
    def _name(self):
        return "Migrations"

    @property
    def field_labels(self):
        return self.MIGRATION_FIELD_DEFS

    @property
    def dao(self):
        return MigrationDAO

    def display_table(self, items=None):
        """Renders the migrations list in a detailed table."""
        if items is None:       # allows user to override display table to display lists of items; full is default
            items = self.items

        table = Table(title=self.title)
        table.add_column("Index", justify="right", style="cyan")
        table.add_column("Migration Name", style="magenta")
        table.add_column("Old Root", style="green")
        table.add_column("New Root", style="yellow")
        table.add_column("Active", style="red")

        for index, migration in enumerate(items, start=1):
            migration_dict = dict(migration)
            is_active = migration_dict.get("is_active")
            active_str = "Yes" if is_active else "No"
            # Choose style based on active status:
            active_style = "green" if is_active else "red"
            # Wrap the active text with the chosen style markup
            active_display = f"[{active_style}]{active_str}[/{active_style}]"

            table.add_row(
                str(index),
                migration_dict.get("name", "N/A"),
                migration_dict.get("old_root", "N/A"),
                migration_dict.get("new_root", "N/A"),
                active_display
            )
        console.print(table)

    def activate_migration(self):
        console.print("[bold blue]Activating migration...[/bold blue]")
        index = self.prompt_for_item("activate")
        try:
            migration = dict(self.items[index])
        except IndexError:
            console.print("[bold red]Invalid selection![/bold red]")
            return self
        try:
            self.dao.set_active_migration(migration["id"])
            console.print(f"[bold green]Migration '{migration['name']}' activated successfully.[/bold green]")
            self.refresh_items()
        except Exception as e:
            console.print(f"[bold red]Error activating migration: {e}[/bold red]")
        return self