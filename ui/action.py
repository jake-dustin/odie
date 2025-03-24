class Action:
    def __init__(self, key, label, func, condition=lambda: True):
        """
        Args:
            :param key (str): The key or shorthand (e.g., "P" for previous).
            :param label (str): The full label (e.g. "Prev Page")
            :param func (callable): The function to execute when this action is selected.
            :param condition (callable): A function returning a boolean indicating whether this action is enabled.
        """
        self.key = key
        self.label = label
        self.func = func
        self.condition = condition

    def is_enabled(self):
        return self.condition()