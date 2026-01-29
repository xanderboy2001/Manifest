#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

from .lib.config import ConfigManager
from .lib.stow import StowManager
from .lib.ui import UIManager
from .lib.utils import (
    ask_to_return,
    print_debug,
    print_error,
    print_menu_output,
    print_success,
)


def handle_stow_menu(stowManager: StowManager, ui: UIManager) -> bool:
    """Run functions from stow menu. Takes selected option as input."""
    while True:
        selected = ui.stow_menu()
        match selected:
            case "list_configs":
                configs = stowManager.list_configs()
                print_menu_output(configs, title="Configs")
            case "add_config":
                config_path = ui.get_path(
                    message="Path to configuration files (/home/user/.config/program)",
                    starting_dir="~",
                )
                output = stowManager.add_config(Path(config_path))
                if output == "error":
                    print_error(f"Could not add {config_path} to Manifest!")
                    ask_to_return()
                else:
                    print_menu_output(output)
                    print_success(f"Successfully added {config_path} to Manifest!")
            case "remove_config":
                pass
            case "deploy_config":
                pass
            case "update_config":
                pass
            case "back" | None:
                return True
            case _:
                print_error(f"Unknown function in stow menu: {selected}")


def main():
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

    ui_theme = cfg.get_opt("theme") or "ansi"
    ui = UIManager(theme=ui_theme)

    # Initial Path Logic
    manifest_path = args.path or cfg.get_opt("manifest_path") or "."
    if cfg.first_run:
        final_path = ui.first_run(manifest_path)

        if final_path != manifest_path:
            cfg.set_opt("manifest_path", final_path)
            manifest_path = final_path

    stow = StowManager(manifest_path)
    stow.ensure_manifest_dir()

    while True:
        main_menu_function = ui.main_menu()
        print_debug(main_menu_function or "")
        match main_menu_function:
            case "stow":
                handle_stow_menu(stowManager=stow, ui=ui)
            case "settings":
                pass
            case "exit" | None:
                print_debug("Goodbye!")
                sys.exit(0)


if __name__ == "__main__":
    main()
