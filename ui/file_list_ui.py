from database import MigrationDAO
from console_instance import console
from ui.paginated_list_ui import PaginatedListUI


class FileListUI(PaginatedListUI):
    """UI for listing files."""

    @property
    def _name(self):
        return "File List UI"

    # def __init__(self, db_manager, files):
    #     self.db_manager = db_manager
    #     self.migration_dao = MigrationDAO()
    #     actions = {
    #         "[F] Flag File": self.flag_file,
    #         "[Q] Quit": self.quit
    #     }
    #     super().__init__("Files", files, actions)
    #
    # def flag_file(self):
    #     """Handles flagging a file."""
    #     index = self.prompt_for_item("Flag")
    #     console.print(f"Flagging file: {self.items[index]['name']}\n")