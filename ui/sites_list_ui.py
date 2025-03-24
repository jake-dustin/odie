from database import SiteDAO
from helpers.validators import non_empty
from ui import Action
from ui.paginated_list_ui import PaginatedListUI
from ui.crud_mixin import CRUDMixin


class SitesListUI(CRUDMixin, PaginatedListUI):
    SITE_FIELD_DEFS = {
        "name": {
            "label": "Site Name",
            "validator": non_empty,
            "default": ""
        }
    }

    def __init__(self, page=1):
        self.items = self.dao.get_all()
        super().__init__(self._name, self.items, page)

    @property
    def default_actions(self):
        site_actions = [
            # Action("C", "Create Site", self.create_item),
            # Action("E", "Edit Site", self.edit_item, condition=self.is_item_modification_enabled),
            Action("P", "Populate Sites", self.populate_sites, condition=lambda: not self.is_item_modification_enabled()),
            # Action("D", "Delete Site", self.delete_item, condition=self.is_item_modification_enabled),
        ]
        return site_actions + super().default_actions

    @property
    def _name(self):
        return "Sites"

    @property
    def field_labels(self):
        return self.SITE_FIELD_DEFS

    @property
    def dao(self):
        return SiteDAO

    def populate_sites(self):
        """Adds the five default file destinations to a migration."""
        site_names = ["Measure", "Dustin & Partners", "Dustin Engineers", "DB2", "Hotie Holdings"]
        for site_name in site_names:
            self.dao.add(name=site_name)
        self.refresh_items()
        return self