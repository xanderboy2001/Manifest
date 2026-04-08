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
        manifest_path (Path): The directory path where the Git repository
            should be initialized or verified.

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
        if self._is_initialized():
            print_debug(f"Git repository already initialized at {self.manifest_path}.")
        else:
            with Status(
                f"Initializing git repository at {self.manifest_path}", spinner="dots"
            ) as status:
                try:
                    cmd = ["git", "init", self.manifest_path]
                    result = subprocess.run(
                        cmd, capture_output=True, text=True, check=True
                    )
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

    def _is_initialized(self) -> bool:
        """Check whether a Git repository already exists at the manifest path.

        Returns:
            bool: True if a .git directory already exists at the manifest path,
                False otherwise.

        """
        git_dir = self.manifest_path / ".git"
        return git_dir.exists() and git_dir.is_dir()

    def stage_all(self) -> bool:
        """Stage all changes in the manifest directory.

        Runs 'git add -A' from the manifest path to prepare all modified,
        added, and deleted files for the next commit.

        Returns:
            bool: True if staging completed without error, False otherwise.

        """
        with Status("Staging all files for commit...", spinner="dots") as status:
            try:
                cmd = ["git", "-C", self.manifest_path, "add", "-A"]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                status.update("[bold]Finishing up...[/]")
                if result.stdout:
                    print_debug(result.stdout)
            except subprocess.CalledProcessError as e:
                print_error(f"Adding unstaged changes failed: {e.stderr}")
                return False
        return True

    def commit(self, message: str) -> bool:
        """Create a commit with all staged changes.

        Args:
            message: The commit message describing the change being recorded.

        Returns:
            bool: True if the commit was created, False otherwise.

        """
        with Status("Committing changes...", spinner="dots") as status:
            try:
                cmd = ["git", "-C", self.manifest_path, "commit", "-m", message]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                status.update("[bold]Finishing up...[/]")
                if result.stdout:
                    print_debug(result.stdout)
            except subprocess.CalledProcessError as e:
                print_error(f"Committing changes failed: {e.stderr}")
                return False
        return True

    def get_status(self) -> list[tuple[str, str]]:
        """Return a list of changed files in the repository.

        Runs 'git status --procelain' and translates the status codes into
            human-readable strings.

        Returns:
            list[tuple[str, str]]: A list of tuples containing
                (status_message, file_path), or an empty list if the working tree is
                clean or an error occurred.

        """
        raw_output = ""
        with Status("Getting status of git repository...", spinner="dots") as status:
            try:
                cmd = ["git", "-C", self.manifest_path, "status", "--short"]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                status.update("[bold]Finishing up...[/]")
                if result.stdout:
                    raw_output = result.stdout
            except subprocess.CalledProcessError as e:
                print_error(f"Failed getting status of git repository: {e.stderr}")

        status_map = {
            "M ": "[yellow]Modified[/]",
            " M": "[yellow]Modified (Unstaged)[/]",
            "MM": "[bold yellow]Modified (Staged & Unstaged)[/]",
            "A ": "[green]Added[/]",
            "AM": "[green]Added & Modified[/]",
            "D ": "[red]Deleted[/]",
            " D": "[red]Deleted (Unstaged)[/]",
            "R ": "[cyan]Renamed[/]",
            "C ": "[blue]Copied[/]",
            "??": "[magenta]Untracked[/]",
            "UU": "[bold red]Merge Conflict[/]",
        }

        status_list = []
        if raw_output:
            for line in raw_output.splitlines():
                if len(line) > 2:
                    status_code = line[:2]
                    file_path = line[2:].strip()

                    readable_status = status_map.get(
                        status_code, f"[grey50]Unknown ({status_code})[/]"
                    )
                    status_list.append((readable_status, file_path))

        return status_list
