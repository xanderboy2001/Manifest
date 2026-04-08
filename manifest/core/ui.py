"""Provide the user interface management system for the Manifest dotfile manager.

This module defines the UIManager class, which leverages Rich and Questionary
to create a themed command-line interface. It handles menu navigation,
interactive path selection, and package-specific icon rendering for a
keyboard-centric user experience.

"""

from pathlib import Path

import questionary
from questionary import Choice
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class UIManager:
    """Handle terminal user interface interactions and styling.

    This class manages the visual presentation of the application, including
    themed menus, path selection prompts, and interactive configuration
    lists using Rich and Questionary.

    Attributes:
        console (Console): The Rich console instance for styled output.
        style (Style): The Questionary style object defined by the active theme.

    """

    def __init__(self, rich_theme):
        """Initialize the UIManager with a specific color theme.

        Args:
            rich_theme (Theme): A Rich Theme instance containing styles for
                'primary', 'secondary', and 'hidden' elements.

        """
        self.rich_theme = rich_theme
        self.console = Console(theme=self.rich_theme)

        styles = rich_theme.styles
        prim = styles.get("primary").color.name if "primary" in styles else "ansicyan"
        sec = (
            styles.get("secondary").color.name
            if "secondary" in styles
            else "ansimagenta"
        )
        hidden = (
            styles.get("hidden").color.name if "hidden" in styles else "ansibrightblack"
        )

        self.questionary_style = questionary.Style([
            ("qmark", f"fg:{prim} bold"),
            ("pointer", f"fg:{prim} bold"),
            ("highlighted", f"fg:{sec} bold"),
            ("instruction", f"fg:{hidden} italic"),
        ])

    def print_title(self) -> None:
        """Display the application branding and title panel.

        Renders a styled "Manifest" banner to the console.

        """
        self.console.print(
            Panel.fit(
                "[bold cyan]Manifest[/bold cyan]: Dotfile Manager", border_style="blue"
            )
        )

    def set_manifest_path(self, current_path: str) -> str:
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

    def prompt_for_git(self) -> bool:
        """Prompt the user to enable Git-based version control.

        Displays an interactive confirmation dialog asking if the user wants to
        manage their manifest with Git, highlighting the benefit of remote
        backups to services like GitHub.

        Returns:
            bool: True if the user elects to use Git, False otherwise

        """
        return questionary.confirm(
            """Would you like to use git to manage version control?
                (This will allow backups to GitHub)""",
            default=True,
        ).ask()

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
            Choice(title="  Git Manager", value="git"),
            Choice(title="󰈆  Exit", value="exit"),
        ]
        self.print_title()
        return questionary.select(
            "Main Menu",
            choices=choices,
            style=self.questionary_style,
            pointer="󰅂",
        ).ask()

    def git_menu(self) -> str | None:
        """Display an interactive Git management menu to the user.

        Uses the questionary library to prompt the user with a list of Git
        actions.

        Returns:
            str | None: The string value corresponding to the user's selection
            (e.g. 'stage', 'commit', 'status', 'back'). Returns None if the
            user interrupts or aborts the prompt.

        """
        choices = [
            Choice(title="Stage all changes", value="stage"),
            Choice(title="Commit all staged changes", value="commit"),
            Choice(title="View Status", value="status"),
            Choice(title="󰌍 Back", value="back"),
        ]
        return questionary.select(
            "Manage Git",
            choices=choices,
            style=self.questionary_style,
            pointer="󰅂",
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
            "Manage Manifest",
            choices=choices,
            style=self.questionary_style,
            pointer="󰅂",
        ).ask()

    def settings_menu(self) -> str | None:
        """Display the settings management sub-menu.

        Presents a list of options for viewing, editing, importing, exporting,
        or resetting application configuration settings.

        Returns:
            str | None: The value of the selected action, or None if cancelled.

        """
        choices = [
            Choice(title="View Current Settings", value="view_settings"),
            Choice(title="Edit Settings", value="edit_settings"),
            Choice(title="Import Existing Settings", value="import_settings"),
            Choice(title="Export Current Settings", value="export_settings"),
            Choice(title="Reset Current Settings to Default", value="reset_settings"),
            Choice(title="󰌍 Back", value="back"),
        ]
        return questionary.select(
            "Manage Settings",
            choices=choices,
            style=self.questionary_style,
            pointer="󰅂",
        ).ask()

    def print_settings_table(self, settings: dict[str, str]) -> None:
        """Display configuration settings in a formatted Rich table.

        Renders a two-column table showing configuration options and their
        current values using the colors defined in the active theme.

        Args:
            settings (dict[str, str]): A dictionary of configuration keys
                and their corresponding values to display.

        """
        if not settings:
            self.console.print("[yellow] No settings found.[/yellow]")
            return
        table = Table(
            title="Settings",
            title_style="secondary",
            border_style="border",
            box=None,
            header_style="primary",
            expand=False,
        )
        table.add_column(
            "Option",
            style="muted",
            justify="left",
        )
        table.add_column(
            "Value",
            style="success",
            justify="right",
        )

        for option, value in settings.items():
            table.add_row(option, str(value))

        self.console.print(table)

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
            message=message, default=initial_path, style=self.questionary_style
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
            style=self.questionary_style,
            pointer="󰅂",
        ).ask()

    def print_git_status_table(self, status: list[tuple[str, str]]) -> None:
        """Render and print a formatted table of the current Git status.

        Args:
            status (list[tuple[str, str]]): A list of tuples where the first
                element is the readable status (e.g., 'Modified', 'Untracked')
                and the second element is the file path.

        """
        table = Table(
            title="Git Status",
            title_style="secondary",
            border_style="primary",
        )
        table.add_column("Status", justify="right")
        table.add_column("File", justify="left")
        for readable_status, file_path in status:
            table.add_row(readable_status, file_path)
        self.console.print(table)

    def get_commit_message(self) -> str:
        """Prompt the user to input a Git commit message.

        Returns:
            str: The commit message entered by the user.

        """
        return questionary.text("Enter a commit message").ask()
