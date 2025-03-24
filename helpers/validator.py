class Validator:
    def __init__(self, validator_fn, action_fn=None):
        """
        :param validator_fn: A function that returns True if valid.
        :param action_fn: An optional function to execute if validation fails.
        """
        self._validator_fn = validator_fn
        self._action_fn = action_fn

    def validate(self, value: str) -> bool:
        if self._validator_fn(value):
            return True
        if self._action_fn is not None:
            return self._action_fn(value)
        return False