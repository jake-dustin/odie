# paginated_list_ui.py
import math

from ui.list_ui import ListUI
from ui.pagination_mixin import PaginationMixin

class PaginatedListUI(PaginationMixin, ListUI):
    @property
    def _name(self):
        return "Paginated List UI"

    def __init__(self, title, items, page):
        ListUI.__init__(self, title, items)
        self.setup_pagination(page)

    @property
    def default_actions(self):
        return self.pagination_actions() + super().default_actions

    @property
    def page_size(self):
        return 10

    @property
    def total_pages(self):
        return math.ceil(len(self.items) / self.page_size)