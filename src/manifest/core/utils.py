"""Provide utility functions for CLI output formatting and user interaction.

This module provides standardized logging, colorful console printing using Rich,
and interactive prompts using Questionary. It applies a consistent Dracula-themed
styling across all UI elements including panels, tables, and status messages.

Attributes:
    pal (dict): The color palette loaded from the global configuration.
    custom_theme (Theme): The Rich theme defining styles for info, success, and errors.
    custom_questionary_style (Style): The styling applied to interactive prompts.
    console (Console): The primary Rich console instance for stdout.
    logger (Logger): The configured Rich logging instance.

"""

import logging

import questionary
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme

console = Console()

logging.basicConfig(
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True, markup=True)],
)
logger = logging.getLogger("rich")


def set_log_level(verbose: bool) -> None:
    """Set the logging level for the application logger.

    Args:
        verbose (bool): If True, sets the log level to DEBUG.
            Otherwise, INFO is used.

    """
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)


def setup_utils_theme(rich_theme: Theme) -> None:
    """Register the application theme with the utility console.

    Updates the global console instance with the provided Rich theme to
    ensure consistent styling across all utility-driven output.

    Args:
        rich_theme (Theme): A rich.theme Theme instance containing the
            application's color definitions.

    """
    global console
    console.push_theme(rich_theme)


def print_error(message: str) -> None:
    """Print an error message to the console with a cross symbol.

    Args:
        message (str): The error message string to display.

    """
    console.print(f"[error]✘ {message}[/error]")


def print_warning(message: str) -> None:
    """Log a warning message using the Rich logging handler.

    Args:
        message (str): The warning string to log.

    """
    logger.warning(f"󰀦 {message}")


def print_debug(message: str) -> None:
    """Log a debug message using the Rich logging handler.

    Args:
        message (str): The debug information string to log.

    """
    logger.debug(message)


def print_success(message: str) -> None:
    """Print a success message to the console with a checkmark symbol.

    Args:
        message (str): The success message string to display.

    """
    console.print(f"[success]✔ {message}[/success]")


def ask_to_return() -> None:
    """Prompt the user to press any key to continue.

    This is typically used to pause execution after displaying data so the
    user can read the output before the screen is cleared or changed.

    """
    questionary.press_any_key_to_continue(
        message="Press any key to return to the previous menu...",
        # style=custom_questionary_style,
    ).ask()


def print_menu_output(data: str | list[str], title: str = "Output") -> None:
    """Display data in a styled Dracula-themed panel or table.

    If the data is a list, it renders as a bulleted table. If the data is a
    string, it renders within a standard Rich Panel. Automatically calls
    `ask_to_return()` after rendering.

    Args:
        data (Union[str, List[str]]): The information to display. Can be a single
            string or a list of strings.
        title (str): The title to display at the top of the panel or table.
            Defaults to "Output".

    """
    if not data:
        console.print(f"[menu.muted]No {title.lower()} found.[/menu.muted]")
        return

    # border_color = pal["border"]
    # title_style = f"{pal['secondary']} bold"

    # Handle lists like a table
    if isinstance(data, list):
        table = Table(
            box=None,
            show_header=False,
            padding=(0, 1),
            # title=f"[{title_style}]{title}[/{title_style}]",
            title=title,
            title_justify="left",
        )
        for item in data:
            # table.add_row(f"[{pal['primary']}]•[/{pal['primary']}]  {item}")
            table.add_row(f"•  {item}")

        console.print(
            Panel(
                table,  # border_style=border_color,
                expand=False,
            )
        )
    else:
        # Handle strings with a Panel
        console.print(
            Panel(
                data,
                # title=f"[{title_style}]{title}[/{title_style}]",
                title=title,
                # border_style=border_color,
                expand=False,
            )
        )

    ask_to_return()
