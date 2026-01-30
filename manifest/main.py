#!/usr/bin/env python3
"""Execute the primary command-line interface for the Manifest dotfile manager.

This module serves as the entry point for the application, handling argument
parsing, configuration loading, and the orchestration of the interactive
terminal UI menus for managing GNU Stow configurations.

"""

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
    """Execute functions selected from the stow management sub-menu.

    Provides a loop that captures user input from the UI and dispatches the
    appropriate StowManager actions, such as listing or adding configurations.

    Args:
        stowManager (StowManager): The manager instance handling Stow logic.
        ui (UIManager): The UI instance handling user interaction and menus.

    Returns:
        bool: True if the user chooses to return to the previous menu.

    """
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
                    ask_to_return()
                else:
                    print_success(f"Successfully added {config_path} to Manifest!")
                    print_menu_output(output, title="Files Stowed")
            case "remove_config":
                config_name = ui.choose_config(
                    configs=stowManager.list_configs(),
                    prompt="Choose a config to remove from Manifest",
                )
                while config_name is None:
                    print_error("Please select a config")
                    config_name = ui.choose_config(
                        configs=stowManager.list_configs(),
                        prompt="Choose a config to remove from Manifest",
                    )
                output = stowManager.remove_config(config_name)
                if output != "error":
                    print_success(f"Successfully removed {config_name} from Manifest!")
                ask_to_return()
            case "deploy_config":
                pass
            case "update_config":
                pass
            case "back" | None:
                return True
            case _:
                print_error(f"Unknown function in stow menu: {selected}")


def main():
    """Initialize the application and run the main event loop.

    Parses command-line arguments, sets up the configuration and UI themes,
    ensures the manifest directory exists, and manages the top-level navigation
    between different application modules.

    """
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
