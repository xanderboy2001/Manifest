"""Provide the user interface management system for the Manifest dotfile manager.

This module defines the UIManager class, which leverages Rich and Questionary
to create a themed command-line interface. It handles menu navigation,
interactive path selection, and package-specific icon rendering for a
keyboard-centric user experience.

"""

from pathlib import Path

import questionary
from questionary import Choice, Style
from rich.console import Console
from rich.panel import Panel

from .config import THEMES


class UIManager:
    """Handle terminal user interface interactions and styling.

    This class manages the visual presentation of the application, including
    themed menus, path selection prompts, and interactive configuration
    lists using Rich and Questionary.

    Attributes:
        console (Console): The Rich console instance for styled output.
        style (Style): The Questionary style object defined by the active theme.

    """

    def __init__(self, theme="dracula"):
        """Initialize the UIManager with a specific color theme.

        Args:
            theme (str): The name of the theme to apply. Defaults to "dracula".

        """
        self.console = Console()

        colors = THEMES.get(theme, THEMES.get("dracula", THEMES["ansi"]))

        self.style = Style(
            [
                ("qmark", f"fg:{colors['primary']} bold"),
                ("question", "bold"),
                ("pointer", f"fg:{colors['primary']} bold"),
                ("highlighted", f"fg:{colors['secondary']} bold"),
                ("selected", f"fg:{colors['success']}"),
                ("instruction", f"fg:{colors['muted']}"),
            ]
        )

    def print_title(self) -> None:
        """Display the application branding and title panel.

        Renders a styled "Manifest" banner to the console.

        """
        self.console.print(
            Panel.fit(
                "[bold cyan]Manifest[/bold cyan]: Dotfile Manager", border_style="blue"
            )
        )

    def first_run(self, current_path: str) -> str:
        """Guide the user through the initial setup process.

        Confirms the default manifest path or allows the user to specify a
        new location for their dotfiles.

        Args:
            current_path (str): The default path suggested for the manifest.

        Returns:
            str: The confirmed or newly entered manifest path.

        """
        self.print_title()
        confirm = questionary.confirm(
            f"Use manifest path: {current_path}?", default=True
        ).ask()

        if not confirm:
            current_path = self.get_path(
                message="Enter the path for your dotfiles to live:",
                starting_dir=current_path,
            )
        return current_path

    def main_menu(self) -> str | None:
        """Display the top-level application navigation menu.

        Presents options for stowing configurations, editing settings, or
        exiting the program.

        Returns:
            str | None: The value associated with the selected menu option.

        """
        choices = [
            Choice(title="󱔗  Stow Configurations", value="stow"),
            Choice(title="  Edit Settings", value="settings"),
            Choice(title="󰈆  Exit", value="exit"),
        ]
        self.print_title()
        return questionary.select(
            "Main Menu", choices=choices, style=self.style, pointer="󰅂"
        ).ask()

    def stow_menu(self) -> str | None:
        """Display the configuration management sub-menu.

        Presents detailed options for managing the manifest, including listing,
        adding, removing, and deploying configurations.

        Returns:
            str | None: The value associated with the selected stow action.

        """
        choices = [
            Choice(
                title="List All Configurations in Manifest (Stowed/Unstowed)",
                value="list_configs",
            ),
            Choice(title="Add Existing Configuration to Manifest", value="add_config"),
            Choice(
                title="Remove Existing Configuration from Manifest",
                value="remove_config",
            ),
            Choice(title="Deploy Configuration from Manifest", value="deploy_config"),
            Choice(title="Update Configuration from Manifest", value="update_config"),
            Choice(title="󰌍 Back", value="back"),
        ]
        return questionary.select(
            "Manage Manifest", choices=choices, style=self.style, pointer="󰅂"
        ).ask()

    def get_path(self, message: str = "Enter Path:", starting_dir: str = "~") -> str:
        """Prompt the user for a filesystem path with autocompletion.

        Args:
            message (str): The prompt message to display. Defaults to "Enter Path:".
            starting_dir (str): The directory to start the path picker in.
                Defaults to "~".

        Returns:
            str: The filesystem path entered by the user.

        """
        initial_path = str(Path(starting_dir).expanduser())
        if not initial_path.endswith("/"):
            initial_path += "/"
        return questionary.path(
            message=message, default=initial_path, style=self.style
        ).ask()

    def choose_config(self, configs: list[str], prompt: str) -> str | None:
        """Display a selection menu for available configuration packages.

        Automatically assigns icons to configurations based on their names
        (e.g., Neovim, Git, Python) and provides a list for user selection.

        Args:
            configs (list[str]): A list of configuration names to display.
            prompt (str): The question or instruction to display to the user.

        Returns:
            str | None: The name of the selected configuration or "back".

        """
        if not configs:
            self.console.print("[yellow]󱈸No configurations found.[/yellow]")
            return None

        # Assign icons based on folder name
        choices = []
        for cfg in configs:
            icon = ""
            if "nvim" in cfg or "vim" in cfg:
                icon = ""
            elif "zsh" in cfg or "fish" in cfg or "bash" in cfg:
                icon = ""
            elif "git" in cfg:
                icon = ""
            elif "tmux" in cfg:
                icon = ""
            elif "python" in cfg:
                icon = ""

            choices.append(Choice(title=f"{icon} {cfg}", value=cfg))
        choices.append(Choice(title="󰌍  Back", value="back"))

        return questionary.select(
            prompt,
            choices=choices,
            style=self.style,
            pointer="󰅂",
        ).ask()
