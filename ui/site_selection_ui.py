from database import SiteDAO
from ui.selection_ui import SelectionUI


class SiteSelectionUI(SelectionUI):
    @property
    def _name(self):
        return "Site Selection"

    @property
    def dao(self):
        return SiteDAO