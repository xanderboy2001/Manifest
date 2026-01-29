import logging
from typing import List, Union

import questionary
from questionary import Style
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

custom_questionary_style = Style(
    [
        ("instruction", f"fg:{pal['muted']} italic"),
        ("qmark", f"fg:{pal['primary']} bold"),
    ]
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


def ask_to_return():
    questionary.press_any_key_to_continue(
        message="Press any key to return to the previous menu...",
        style=custom_questionary_style,
    ).ask()


def print_menu_output(data: Union[str, List[str]], title: str = "Output") -> None:
    """Prints a Dracula-themed panel or list."""
    if not data:
        console.print(f"[menu.muted]No {title.lower()} found.[/menu.muted]")
        return

    border_color = pal["border"]
    title_style = f"{pal['secondary']} bold"

    # Handle lists like a table
    if isinstance(data, list):
        table = Table(
            box=None,
            show_header=False,
            padding=(0, 1),
            title=f"[{title_style}]{title}[/{title_style}]",
            title_justify="left",
        )
        for item in data:
            table.add_row(f"[{pal['primary']}]•[/{pal['primary']}]  {item}")

        console.print(Panel(table, border_style=border_color, expand=False))
    else:
        # Handle strings with a Panel
        console.print(
            Panel(
                data,
                title=f"[{title_style}]{title}[/{title_style}]",
                border_style=border_color,
                expand=False,
            )
        )

    ask_to_return()
