from rich.table import Table

from console_instance import console
from database import ProjectDAO, SiteDAO, ClientDAO
from helpers.validators import non_empty
from ui import Action
from ui.paginated_list_ui import PaginatedListUI
from ui.crud_mixin import CRUDMixin


class ProjectsListUI( PaginatedListUI, CRUDMixin):
    PROJECT_FIELD_DEFS = {
        "name": {
            "label": "Project Name",
            "validator": non_empty,
            "default": ""
        },
        "site_id": {
            "label": "Site",
            "selection_ui": lambda: __import__("ui.site_selection_ui", fromlist=["SiteSelectionUI"]).SiteSelectionUI(),
        },
        "client_id": {
            "label": "Client",
            "selection_ui": lambda: __import__("ui.client_selection_ui", fromlist=["ClientSelectionUI"]).ClientSelectionUI(),
        }
    }

    def __init__(self, page=1):
        self.client_lookup = {}
        self.site_lookup = {}
        self.items = [{}]
        self.refresh_items()
        super().__init__(self._name, self.items, page)

    @property
    def default_actions(self):
        project_actions = [
            Action("C", "Create Project", self.create_item),
            Action("E", "Edit Project", self.edit_item, condition=self.is_item_modification_enabled),
            Action("D", "Delete Project", self.delete_item, condition=self.is_item_modification_enabled),
        ]
        return project_actions + super().default_actions

    @property
    def _name(self):
        return "Projects"

    @property
    def field_labels(self):
        return self.PROJECT_FIELD_DEFS

    @property
    def dao(self):
        return ProjectDAO

    def display_table(self, items=None):
        if items is None:
            items = self.items

        table = Table(title=self.title)
        table.add_column("Index", justify="right", style="cyan")
        table.add_column("Project Name", style="magenta")
        table.add_column("Site", style="green")
        table.add_column("Client", style="yellow")

        for index, item in enumerate(items, start=1):
            project_dict = dict(item)
            table.add_row(
                str(index),
                project_dict["name"],
                self.site_lookup.get(project_dict["site_id"], ""),
                self.client_lookup.get(project_dict["client_id"], ""),
            )

        console.print(table)

    # overrides implementation in retrieval_mixin.py
    def refresh_items(self):
        sites = SiteDAO.get_all()
        clients = ClientDAO.get_all()

        self.site_lookup = {site["id"]: site["name"] for site in sites}
        self.client_lookup = {client["id"]: client["name"] for client in clients}

        self.items = ProjectDAO.get_all()
