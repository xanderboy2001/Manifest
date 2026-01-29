import shutil
import subprocess
from pathlib import Path
from typing import List

from .utils import print_debug, print_error


class StowManager:
    def __init__(self, manifest_path: str) -> None:
        self.manifest_path = Path(manifest_path).expanduser()
        self._check_stow_installed()

    def _check_stow_installed(self) -> None:
        if not shutil.which("stow"):
            print_error("GNU Stow could not be found")
            exit(1)

    def list_configs(self) -> List[str]:
        """Lists subdirectories in the manifest path (excluding .git)."""
        if not self.manifest_path.exists():
            return []

        configs = []
        for item in self.manifest_path.iterdir():
            if item.is_dir() and item.name != ".git":
                configs.append(item.name)
        return sorted(configs)

    def dry_run(self, target_package: str, target_dir: str = None) -> None:
        """Runs stow in simulation mode."""
        if not self.manifest_path.exists():
            print_error(f"'{self.manifest_path}' is not a valid path!")
            return

        # Default target is usually the parent of the manifest, or home
        # Adjusting logic to match typical Stow usage (stow into HOME)
        # unless overridden
        target_dir = Path(target_dir).expanduser() if target_dir else Path.home()

        if not (self.manifest_path / target_package).exists():
            print_error(f"'{target_package}' is not a valid package in manifest!")
            return

        cmd = [
            "stow",
            "--simulate",
            "--dir",
            str(self.manifest_path),
            "--target",
            str(target_dir),
            target_package,
        ]

        #        print(f"{Colors.BLUE}Running: {' '.join(cmd)}{Colors.END}")
        print_debug("Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print_error(result.stderr)
        else:
            print(result.stdout)
            # print(f"{Colors.GREEN}Dry run complete.{Colors.END}")
            print_debug("Dry run complete.")
