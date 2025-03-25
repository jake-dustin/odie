from database import ClientDAO
from ui.selection_ui import SelectionUI


class ClientSelectionUI(SelectionUI):
    @property
    def _name(self):
        return "Client Selection"

    @property
    def dao(self):
        return ClientDAO