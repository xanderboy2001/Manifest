import questionary
from questionary import Choice, Style
from rich.console import Console
from rich.panel import Panel


class UIManager:
    def __init__(self):
        self.console = Console()

        self.style = Style(
            [
                ("qmark", "fg:#ff79c6 bold"),
                ("question", "bold"),
                ("pointer", "fg:#ff79c6 bold"),
                ("highlighted", "fg:#8b39fd bold"),
                ("selected", "fg:#50fa7b"),
                ("instruction", "fg:#6272a4"),
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
