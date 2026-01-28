#!/usr/bin/env python3
import argparse
from enum import nonmember
from pathlib import Path
from lib.config import ConfigManager
from lib.stow import StowManager
from lib.ui import UIManager
from lib.utils import Colors


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
    manifest_path = args.path or cfg.get_opt("manifest_path")

    ui = UIManager()

    final_path = ui.init_ui(manifest_path)
    if final_path != manifest_path:
        cfg.set_opt("manifest_path", final_path)
        manifest_path = final_path

    stow = StowManager(manifest_path)

    configs = stow.list_configs()
    selected = ui.choose_config(configs)

    if selected:
        print(f"Selected config: {Colors.CYAN}{selected}{Colors.END}")

        stow.dry_run(selected, args.target)


if __name__ == "__main__":
    main()
