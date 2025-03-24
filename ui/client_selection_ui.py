from database import ClientDAO
from ui.selection_ui import SelectionUI


class ClientSelectionUI(SelectionUI):
    @property
    def _name(self):
        return "Client Selection"

    def __init__(self):
        self.items = ClientDAO.get_all()
        super().__init__("Clients", self.items, 1)