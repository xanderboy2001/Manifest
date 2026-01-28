import questionary
from rich.console import Console
from rich.panel import Panel


class UIManager:
    def __init__(self):
        self.console = Console()

    def init_ui(self, current_path: str) -> str:
        """Greeting and path confirmation."""
        self.console.print(
            Panel.fit(
                "[bold cyan]Manifest[/bold cyan]: Dotfile Manager", border_style="blue"
            )
        )

        # Interactive confirmation/update of path
        if not current_path:
            current_path = "."

        confirm = questionary.confirm(
            f"Use manifest path: {current_path}?", default=True
        ).ask()

        if not confirm:
            current_path = questionary.path(
                "Enter the path to your dotfiles:", default=current_path
            ).ask()

        return current_path

    def choose_config(self, configs: list[str]) -> str | None:
        """Keyboard-centric selection using questionary."""
        if not configs:
            self.console.print("[yellow]No configurations found.[/yellow]")
            return None

        selected = questionary.select(
            "Which configuration would you like to stow?",
            choices=configs,
            use_shortcut_keys=True,
        ).ask()

        return selected
