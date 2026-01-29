from rich.console import Console


def print_error(message: str) -> None:
    error_console = Console(stderr=True, style="bold red")
    error_console.print(message)


def print_debug(message: str) -> None:
    debug_console = Console()
    debug_console.log(message)
