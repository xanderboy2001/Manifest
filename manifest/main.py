#!/usr/bin/env python3
import argparse

from rich.console import Console

from .lib.config import ConfigManager
from .lib.stow import StowManager
from .lib.ui import UIManager


def main():
    console = Console()
    parser = argparse.ArgumentParser(description="Manifest: Dotfile Manager")
    parser.add_argument(
        "--path", "-p", help="Override default manifest path", default=None
    )
    parser.add_argument(
        "--target", "-t", help="Override target directory", default=None
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Simulate stow operation"
    )
    args = parser.parse_args()

    cfg = ConfigManager()
    ui = UIManager()

    # Initial Path Logic
    manifest_path = args.path or cfg.get_opt("manifest_path") or "."
    if cfg.first_run:
        final_path = ui.first_run(manifest_path)

        if final_path != manifest_path:
            cfg.set_opt("manifest_path", final_path)
            manifest_path = final_path

    stow = StowManager(manifest_path)
    stow.ensure_manifest_dir()
    configs = stow.list_configs()
    selected = ui.choose_config(configs)

    if selected:
        console.print(f"\n[bold green]▶[/bold green] Selected: [cyan]{selected}[/cyan]")

        # Provide feedback via rich during the stow operation
        with console.status(f"[bold blue]Stowing {selected}...", spinner="dots"):
            stow.dry_run(selected, args.target)

        console.print("[bold green]Success![/bold green] Operation completed.")


if __name__ == "__main__":
    main()
