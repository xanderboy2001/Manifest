import shutil
import subprocess
from pathlib import Path
from typing import List, Optional

from rich.status import Status

from .utils import print_debug, print_error


class StowManager:
    def __init__(self, manifest_path: str | Path) -> None:
        self.manifest_path = Path(manifest_path).expanduser()
        self._check_stow_installed()

    def _check_stow_installed(self) -> None:
        if not shutil.which("stow"):
            print_error("GNU Stow could not be found")
            exit(1)

    def ensure_manifest_dir(self) -> None:
        """Creates the manifest directory if it doesn't exist."""
        if not self.manifest_path.exists():
            print_debug(f"Creating manifest directory ar {self.manifest_path}")
            self.manifest_path.mkdir(parents=True, exist_ok=True)

    def list_configs(self) -> List[str]:
        """Lists subdirectories in the manifest path (excluding .git)."""
        if not self.manifest_path.exists():
            return []

        configs = []
        for item in self.manifest_path.iterdir():
            if item.is_dir() and item.name != ".git":
                configs.append(item.name)
        return sorted(configs)

    def dry_run(self, target_package: str, target_dir: Optional[str] = None) -> None:
        """Runs stow in simulation mode."""
        if not self.manifest_path.exists():
            print_error(f"'{self.manifest_path}' is not a valid path!")
            return

        # Default target is usually the parent of the manifest, or home
        # Adjusting logic to match typical Stow usage (stow into HOME)
        # unless overridden
        dest_path = Path(target_dir).expanduser() if target_dir else Path.home()

        if not (self.manifest_path / target_package).exists():
            print_error(f"'{target_package}' is not a valid package in manifest!")
            return

        cmd = [
            "stow",
            "--simulate",
            "--dir",
            str(self.manifest_path),
            "--target",
            str(dest_path),
            target_package,
        ]
        with Status(
            f"[bold green]Simulating stow for {target_package}...", spinner="dots"
        ) as status:
            try:
                print_debug(f"Running: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                status.update("[bold blue]Finishing up...")
                if result.stdout:
                    print(result.stdout)
                print_debug("Dry run complete.")
            except subprocess.CalledProcessError as e:
                print_error(f"Stow failed: {e.stderr}")
            except Exception:
                import logging

                logging.getLogger("rich").exception(
                    "An unexpected error occurred during dry run"
                )
