from console_instance import console
from ui.action import Action
from ui.paginated_list_ui import PaginatedListUI
from ui.retrieval_mixin import RetrievalMixin


class SelectionUI(PaginatedListUI, RetrievalMixin):
    def __init__(self, title=None, page=1):
        if title is None:
            title = self._name

        self.items = self.dao.get_all()
        super().__init__(title, self.items, page)

    @property
    def _name(self):
        return "Selection"

    @property
    def default_actions(self):
        selection_action = Action("S", "Select", self.select_item)
        return [selection_action] + super().default_actions

    def select_item(self):
        index = self.prompt_for_item("select")
        try:
            self.result = dict(self.items[index])
            console.print(f"[bold green]Selected item: {self.result.get('name', 'N/A')}[/bold green]")
        except IndexError:
            console.print(f"[bold red]Selected item not found[/bold red]")
        return self

    def get_result(self):
        return getattr(self, "result", None)