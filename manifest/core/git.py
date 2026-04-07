"""Provide Git repository integration for the Manifest dotfile manager.

This module defines the GitManager class, which automates the initialization
and management of a Git-based version control system within the manifest directory.
It ensures environment compatibility by verifying Git installation
and handles repository setup through subprocess orchestration.
"""

import shutil
import subprocess
from pathlib import Path

from rich.status import Status

from .utils import print_debug, print_error


class GitManager:
    """Manage Git repository operations for the manifest directory.

    This class ensures Git is installed on the system and handles the
    initialization and maintenance of a Git repository within the
    dotfile manifest directory.

    Attributes:
        manifest_path (Path): The filesystem path to the manifest repository.

    """

    def __init__(self, manifest_path: str | Path) -> None:
        """Initialize the GitManager and the underlying Git repository.

        Validates Git installation and attempts to run 'git init' at the
        specified path. Displays a visual status spinner during the process.

        Args:
            manifest_path: The directory path where the Git repository
                should be initialized.

        """
        self._check_git_installed()
        self.manifest_path = Path(manifest_path).expanduser()
        with Status(
            f"Initializing git repository at {self.manifest_path}", spinner="dots"
        ) as status:
            try:
                cmd = ["git", "init", self.manifest_path]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                status.update("[bold]Finishing Up...[/]")
                if result.stdout:
                    print_debug(result.stdout)
            except subprocess.CalledProcessError as e:
                print_error(f"Initializing git repository failed: {e.stderr}")

    def _check_git_installed(self) -> None:
        """Verify that the Git executable is available in the system PATH.

        Raises:
            SystemExit: If the 'git' command is not found on the system.

        """
        if not shutil.which("git"):
            print_error("Git could not be found. Please install it to continue")
            raise SystemExit
