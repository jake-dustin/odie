class RetrievalMixin:
    @property
    def dao(self):
        raise NotImplementedError("Subclasses must provide dao.")

    def refresh_items(self):
        """Refresh self.items from the data source. Can be overridden by subclass."""
        self.items = self.dao.get_all()