#!/usr/bin/env python3
import argparse

from .lib.config import ConfigManager
from .lib.stow import StowManager
from .lib.ui import UIManager
from .lib.utils import print_debug


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

    menu_function = ui.main_menu()
    print_debug(menu_function or "")


if __name__ == "__main__":
    main()
