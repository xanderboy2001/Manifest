import logging
from typing import List, Union

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme

from .config import THEMES

pal = THEMES["dracula"]

custom_theme = Theme(
    {
        "info": f"{pal['secondary']}",  # Purple
        "warning": f"{pal['warning']}",  # Orange
        "error": f"{pal['error']} bold",  # Red
        "success": f"{pal['success']}",  # Green
        "menu.title": f"{pal['secondary']} bold",  # Purple bold
        "menu.item": f"{pal['primary']}",  # Pink
        "menu.muted": f"{pal['muted']}",  # Grey
    }
)

console = Console(theme=custom_theme)

logging.basicConfig(
    level="DEBUG",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True, markup=True)],
)
logger = logging.getLogger("rich")


def print_error(message: str) -> None:
    console.print(f"[error]✘ {message}[/error]")


def print_debug(message: str) -> None:
    logger.debug(message)


def print_success(message: str) -> None:
    console.print(f"[success]✔ {message}[/success]")


def print_menu_output(data: Union[str, List[str]], title: str = "Output") -> None:
    """Prints a Dracula-themed panel or list."""
    if not data:
        console.print(f"[menu.muted]No {title.lower()} found.[/menu.muted]")
        return

    # Handle lists like a table
    if isinstance(data, list):
        table = Table(
            box=None,
            show_header=False,
            padding=(0, 1),
            title=f"[menu.title]{title}[/menu.title]",
            title_justify="left",
        )
        for item in data:
            table.add_row(f"[menu.item]•[/menu.item]  {item}")

        console.print(Panel(table, border_style="menu.border", expand=False))
        return

    # Handle strings with a Panel
    console.print(
        Panel(
            data,
            title=f"[menu.title]{title}[/menu.title]",
            border_style="menu.border",
            expand=False,
        )
    )
