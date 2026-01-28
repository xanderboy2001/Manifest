import questionary
from rich.console import Console
from rich.panel import Panel


class UIManager:
    def __init__(self):
        self.console = Console()

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
