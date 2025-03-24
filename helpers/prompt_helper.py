import os

from rich.prompt import Prompt


def prompt_for_fields(field_defs, current_values=None):
    """
    Prompts for each field defined in field_defs.

    Args:
        field_defs (dict): Mapping of field keys to a dict with keys:
                           "label" (str), "validator" (callable), and "error" (str).
        current_values (dict, optional): If provided, used as default values for editing.

    Returns:
        dict: Collected field values.
    """
    results = {}
    for field, config in field_defs.items():
        label = config.get("label", field)
        validator = config.get("validator", lambda x: True)
        default_value = config.get("default", "") if current_values is None else current_values.get(field, "")
        is_path = config.get("is_path", False)
        prompt_text = f"{label}"

        while True:
            value = Prompt.ask(prompt_text, default=default_value)
            if is_path and default_value and not os.path.isabs(value):
                value = os.path.join(default_value, value)
            if hasattr(validator, "validate"):
                valid = validator.validate(value)
            else:
                valid = validator(value)
            if valid:
                results[field] = value
                break
            else:
                return
    return results