# pagination_mixin.py
from console_instance import console
from ui.action import Action


# noinspection PyAttributeOutsideInit
class PaginationMixin:
    def setup_pagination(self, page, total_pages):
        self.page = page
        self.total_pages = total_pages

    def is_prev_enabled(self):
        return self.page > 1

    def is_next_enabled(self):
        return self.page < self.total_pages

    def prev_page(self):
        if self.is_prev_enabled():
            self.page -= 1
            console.print(f"[bold cyan]Moved to page {self.page}[/bold cyan]")
        else:
            console.print("[dim]Already at the first page.[/dim]")
        return self

    def next_page(self):
        if self.is_next_enabled():
            self.page += 1
            console.print(f"[bold cyan]Moved to page {self.page}[/bold cyan]")
        else:
            console.print("[dim]Already at the last page.[/dim]")
        return self

    def pagination_actions(self):
        return [
            Action("P", "Prev Page", self.prev_page, condition=self.is_prev_enabled),
            Action("N", "Next Page", self.next_page, condition=self.is_next_enabled),
        ]