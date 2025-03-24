from rich.table import Table

from database import ClientDAO
from helpers.validators import non_empty
from ui import Action
from ui.paginated_list_ui import PaginatedListUI
from ui.crud_mixin import CRUDMixin


class ClientsListUI(CRUDMixin, PaginatedListUI):
    CLIENT_FIELD_DEFS = {
        "name": {
            "label": "Client Name",
            "validator": non_empty,
            "default": ""
        }
    }

    def __init__(self, page=1):
        self.items = self.dao.get_all()
        super().__init__(self._name, self.items, page)

    @property
    def default_actions(self):
        client_actions = [
            Action("C", "Create Client", self.create_item),
            Action("E", "Edit Client", self.edit_item, condition=self.is_item_modification_enabled),
            Action("D", "Delete Client", self.delete_item, condition=self.is_item_modification_enabled),
        ]
        return client_actions + super().default_actions

    @property
    def _name(self):
        return "Clients"

    @property
    def field_labels(self):
        return self.CLIENT_FIELD_DEFS

    @property
    def dao(self):
        return ClientDAO