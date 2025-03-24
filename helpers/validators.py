import re
from pathlib import Path

from rich.prompt import Prompt

from console_instance import console
from helpers.validator import Validator


def _compose_validation_fn_with_errors(*validation_tuples):
    """
    Compose multiple validators where each is a tuple of
    (validator_fn, error_message). For a given value, each validator is run in sequence.
    If any validator fails, its associated error message is printed and the composite function returns False.
    Otherwise, returns True.
    """
    def validation_fn(value):
        for fn, msg in validation_tuples:
            if not fn(value):
                _print_error_msg(msg)
                return False
        return True
    return validation_fn

def _print_error_msg(msg: str) -> None:
    console.print(f"[bold red]{msg}[/bold red]")

def _compose_validation_fn(*validation_funcs):
    def validation_fn(value):
        return all(fn(value) for fn in validation_funcs)
    return validation_fn

def _non_empty(value: str) -> bool:
    return len(value) > 0

def _path_pattern_is_valid(value: str) -> bool:
    pattern = r"^\/(?:[^\/0]+\/?)+$"
    return bool(re.match(pattern, value))

def _directory_exists_or_prompt(value: str) -> bool:
    path = Path(value)
    if path.is_dir():
        return True
    return False

def _create_directory(value: str) -> bool:
    path = Path(value)
    response = Prompt.ask(f"Directory {value} was not found. Create it?", choices=["Y", "N"], default="Y")
    if response.lower() == "y":
        try:
            path.mkdir(parents=True, exist_ok=True)
            console.print(f"[green]Directory {value} was created.[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Failed to create {value}. {e}")
            return False
    else:
        return False

non_empty = Validator(
    validator_fn=_compose_validation_fn_with_errors(
        (_non_empty, "Value may not be empty.")
    )
)

validate_and_create_directory = Validator(
    validator_fn=
        _compose_validation_fn_with_errors(
            (_non_empty, "Value may not be empty."),
            (_path_pattern_is_valid, "Invalid directory path."),
            (_directory_exists_or_prompt, "Directory does not exist.")
        ),
    action_fn=_create_directory
)