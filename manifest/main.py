#!/usr/bin/env python3
import argparse
import sys

from .lib.config import ConfigManager
from .lib.stow import StowManager
from .lib.ui import UIManager
from .lib.utils import print_debug, print_error


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

    main_menu_function = ui.main_menu()
    print_debug(main_menu_function or "")
    match main_menu_function:
        case "stow":
            stow_menu_function = ui.stow_menu()
            if stow_menu_function:
                print_debug(stow_menu_function)
            else:
                print_error(f"{stow_menu_function} not found!")
        case "settings":
            pass
        case "exit":
            print_debug("Goodbye!")
            sys.exit(0)


if __name__ == "__main__":
    main()
