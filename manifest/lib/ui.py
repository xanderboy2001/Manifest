import questionary
from questionary import Choice, Style
from rich.console import Console
from rich.panel import Panel


class UIManager:
    def __init__(self, theme="dracula"):
        self.console = Console()

        themes = {
            "dracula": {
                "primary": "#ff79c6",  # Pink
                "secondary": "#8b39fd",  # Cyan
                "success": "#50fa7b",  # Green
                "muted": "#6272a4",  # Gray
            },
            "ansi": {
                "primary": "ansimagenta",
                "secondary": "ansicyan",
                "success": "ansigreen",
                "muted": "ansibrightblack",
            },
        }

        colors = themes.get(theme, themes["dracula"])

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
        """Greeting and path confirmation."""
        self.console.print(
            Panel.fit(
                "[bold cyan]Manifest[/bold cyan]: Dotfile Manager", border_style="blue"
            )
        )

    def first_run(self, current_path: str) -> str:
        self.print_title()
        confirm = questionary.confirm(
            f"Use manifest path: {current_path}?", default=True
        ).ask()

        if not confirm:
            current_path = questionary.path(
                "Enter the path for your dotfiles to live:", default=current_path
            ).ask()
        return current_path

    def main_menu(self) -> str | None:
        """Entry point for program. Select function."""
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
        """Entry point for stow-related functions"""
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
            Choice(title="󰌍Back", value="back"),
        ]
        return questionary.select(
            "Manage Manifest", choices=choices, style=self.style, pointer="󰅂"
        ).ask()

    def choose_config(self, configs: list[str]) -> str | None:
        """Keyboard-centric selection using questionary."""
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
            "Which configuration would you like to stow?",
            choices=choices,
            style=self.style,
            pointer="󰅂",
        ).ask()
