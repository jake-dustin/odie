from database import ProjectDAO
from helpers.validators import non_empty
from ui import Action
from ui.paginated_list_ui import PaginatedListUI
from ui.crud_mixin import CRUDMixin


class ProjectsListUI(CRUDMixin, PaginatedListUI):
    PROJECT_FIELD_DEFS = {
        "name": {
            "label": "Project Name",
            "validator": non_empty,
            "default": ""
        },
        "site_id": {
            "label": "Site",
            "selection_ui": lambda: __import__("ui.client_selection_ui", fromlist=["ClientSelectionUI"]).ClientSelectionUI,
        },
        "client_id": {
            "label": "Client",
        }
    }

    def __init__(self, page=1):
        self.items = self.dao.get_all()
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
    def field_labels(self):
        return self.PROJECT_FIELD_DEFS

    @property
    def dao(self):
        return ProjectDAO