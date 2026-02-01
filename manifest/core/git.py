import shutil
import subprocess
from pathlib import Path

from rich.status import Status

from .utils import print_debug, print_error


class GitManager:
    def __init__(self, manifest_path: str | Path) -> None:
        self.manifest_path = Path(manifest_path).expanduser()

    def _check_git_installed(self) -> None:
        if not shutil.which("git"):
            print_error("Git could not be found. Please install it to continue")
            exit(1)

    def initialize_repo(self) -> None:
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
                return "error"
            return "success"
