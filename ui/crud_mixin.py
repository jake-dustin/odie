# ui/crud_mixin.py
from rich.prompt import Prompt

from helpers.prompt_helper import prompt_for_fields
from console_instance import console


# noinspection PyAttributeOutsideInit
class CRUDMixin:
    @property
    def field_labels(self):
        """
        Return a dictionary mapping field keys to prompt labels.
        Subclasses must override this property.
        """
        raise NotImplementedError("Subclasses must provide field_labels.")

    @property
    def dao(self):
        raise NotImplementedError("Subclasses must provide dao.")

    def create_item(self):
        console.print(f"[bold blue]Creating new {self._name}...[/bold blue]")
        data = prompt_for_fields(self.field_labels)
        try:
            # Each subclass should implement self.dao_add() to add the item.
            self.dao_add(**data)
            console.print(f"[bold green]{self._name} created successfully.[/bold green]")
            self.refresh_items()
        except Exception as e:
            console.print(f"[bold red]Error creating {self._name}: {e}[/bold red]")
        return self

    def edit_item(self):
        console.print(f"[bold blue]Editing {self._name}...[/bold blue]")
        index = self.prompt_for_item("edit")
        try:
            # Assume the current item can be converted to a dict
            current_item = dict(self.items[index])
        except IndexError:
            console.print("[bold red]Invalid selection![/bold red]")
            return self

        # Prompt for new values, using current_item as defaults
        updated_data = prompt_for_fields(self.field_labels, current_values=current_item)
        self.display_table([updated_data])

        # Only include fields that have changed
        changes = {k: v for k, v in updated_data.items() if v != current_item.get(k)}
        if not changes:
            console.print("[bold yellow]No changes made.[/bold yellow]")
            return self

        confirmation = Prompt.ask("Commit changes?", default="Y", choices=["Y", "N"])
        if confirmation.upper() == "N":
            console.print("[bold yellow]Discarding changes.[/bold yellow]")
            return self

        try:
            # Each subclass should implement self.dao_update() for updating.
            self.dao_update(current_item["id"], **changes)
            console.print(f"[bold green]{self._name} updated successfully.[/bold green]")
            self.refresh_items()
        except Exception as e:
            console.print(f"[bold red]Error editing {self._name}: {e}[/bold red]")
        return self

    def delete_item(self):
        console.print(f"[bold blue]Deleting {self._name}...[/bold blue]")
        index = self.prompt_for_item("delete")
        try:
            item = self.items[index]
        except IndexError:
            console.print("[bold red]Invalid selection![/bold red]")
            return self
        try:
            # Each subclass should implement self.dao_delete()
            self.dao_delete(item["id"])
            console.print(f"[bold green]{self._name} deleted successfully.[/bold green]")
            self.refresh_items()
        except Exception as e:
            console.print(f"[bold red]Error deleting {self._name}: {e}[/bold red]")
        return self

    def is_item_modification_enabled(self):
        return len(self.items) > 0

    # The following methods can be implemented by subclasses:
    def dao_add(self, **data):
        self.dao.add(**data)

    def dao_update(self, item_id, **changes):
        self.dao.update(item_id, **changes)

    def dao_delete(self, item_id):
        self.dao.delete(item_id)

    def refresh_items(self):
        """Refresh self.items from the data source. Can be overridden by subclass."""
        self.items = self.dao.get_all()