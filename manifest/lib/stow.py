"""Manage dotfiles using GNU Stow.

This module provides the StowManager class, which handles the organization,
addition, and listing of configuration packages within a dotfile manifest
directory using GNU Stow for symbolic link management.

"""

import shutil
import subprocess
from os import walk
from os.path import islink, join, relpath
from pathlib import Path
from shutil import move

from rich.status import Status

from .utils import print_debug, print_error


class StowManager:
    """Manage the lifecycle of dotfile packages using GNU Stow.

    This class orchestrates the movement of local configuration files into a
    centralized manifest directory and manages their symbolic links. It
    ensures the environment is prepared for Stow operations and provides
    utilities for auditing existing configurations.

    Attributes:
        manifest_path (Path): The expanded filesystem path to the dotfile
            repository.

    """

    def __init__(self, manifest_path: str | Path) -> None:
        """Initialize the StowManager with a manifest path.

        Args:
            manifest_path (str | Path): The directory where dotfile packages are
                stored.

        """
        self.manifest_path = Path(manifest_path).expanduser()
        self._check_stow_installed()

    def _check_stow_installed(self) -> None:
        """Verify that GNU Stow is installed on the system.

        Exits the program with an error message if the 'stow' executable is
        not found in the system PATH.

        """
        if not shutil.which("stow"):
            print_error("GNU Stow could not be found. Please install it to continue.")
            exit(1)

    def ensure_manifest_dir(self) -> None:
        """Create the manifest directory if it does not exist.

        Recursively creates the directory structure specified by the
        manifest_path attribute.

        """
        if not self.manifest_path.exists():
            print_debug(f"Creating manifest directory ar {self.manifest_path}")
            self.manifest_path.mkdir(parents=True, exist_ok=True)

    def list_configs(self) -> list[str]:
        """List subdirectories in the manifest path.

        Iterates through the manifest directory to find available configuration
        packages, excluding the '.git' directory.

        Returns:
            List[str]: A sorted list of package names (subdirectory names).

        """
        if not self.manifest_path.exists():
            return []

        configs = []
        for item in self.manifest_path.iterdir():
            if item.is_dir() and item.name != ".git":
                configs.append(item.name)
        return sorted(configs)

    def add_config(self, config_path: Path) -> str | list[str]:
        """Add existing configuration files to the manifest.

        Moves the specified configuration directory into the manifest structure
        and then uses GNU Stow to symlink it back to its original location.

        Args:
            config_path (Path): The filesystem path to the configuration
                directory to be managed.

        Returns:
            str | List[str]: A list of relative paths of the files added if
                successful, or the string "error" if an issue occurred.

        """
        if not config_path.exists():
            print_error(f"Path does not exist: {config_path}")
            return "error"
        if islink(config_path):
            print_error(f"{config_path} is a symlink!")
            return "error"

        pkg_name = config_path.name
        rel_to_dotfiles_parent = relpath(config_path, self.manifest_path.parent)
        new_location = self.manifest_path / pkg_name / rel_to_dotfiles_parent
        config_files = []
        for root, _, files in walk(config_path):
            for name in files:
                full_path = join(root, name)
                if islink(full_path):
                    print_error(
                        f"Cannot add {full_path}: \
                            Symlinks inside configs are not supported."
                    )
                    return "error"
                config_files.append(relpath(full_path, config_path))
        try:
            new_location.parent.mkdir(parents=True, exist_ok=True)
            move(str(config_path), str(new_location.parent))
            self.deploy_config(pkg_name)
        except Exception as e:
            print_error(f"Unexpected error: {str(e)}")
            return "error"

    def remove_config(self, config_name: str) -> str:
        """Remove a configuration package from the manifest and restore its files.

        This method unlinks the package using GNU Stow, moves the physical files
        back to their original location in the parent directory of the manifest,
        and deletes the package directory from the manifest.

        Args:
            config_name (str): The name of the configuration package to remove.

        Returns:
            str: A status string indicating "success" or "error".

        """
        if config_name not in self.list_configs():
            print_error(f"Config not found in Manifest: {config_name}")
            return "error"
        with Status(
            f"Removing {config_name} from Manifest...", spinner="dots"
        ) as status:
            try:
                pkg_dir = self.manifest_path / config_name
                cmd = ["stow", "--dir", self.manifest_path, "--delete", config_name]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                status.update("[bold]Finishing up...[/]")
                if result.stdout:
                    print_debug(result.stdout)
                payload_items = [x for x in pkg_dir.iterdir() if x.name != ".git"]

                if not payload_items:
                    print_error(f"No content found in {pkg_dir}")
                    return "error"

                for item in payload_items:
                    target_root = self.manifest_path.parent
                    destination = target_root / item.name

                    if item.is_dir() and destination.exists():
                        for subitem in item.iterdir():
                            move(str(subitem), str(destination))
                    else:
                        move(str(item), str(target_root))

                shutil.rmtree(pkg_dir)

                return "success"
            except subprocess.CalledProcessError as e:
                print_error(f"Stow failed: {e.stderr}")
                return "error"
            except Exception as e:
                print_error(f"Unexpected error: {str(e)}")
                return "error"

    def deploy_config(self, config_name: str) -> str:
        """Deploy a configuration package from the manifest using GNU Stow.

        This method executes the stow command to create symbolic links for the
        specified package from the manifest directory to the target environment.

        Args:
            config_name (str): The name of the configuration package to deploy.

        Returns:
            str: A status string indicating "success" or "error".

        """
        if config_name not in self.list_configs():
            print_error(f"Config not found in Manifest: {config_name}")
            return "error"
        with Status(
            f"Deploying {config_name} from Manifest...", spinner="dots"
        ) as status:
            try:
                cmd = ["stow", "--dir", self.manifest_path, "--stow", config_name]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                status.update("[bold]Finishing Up...[/]")
                if result.stdout:
                    print_debug(result.stdout)
            except subprocess.CalledProcessError as e:
                print_error(f"Stow failed: {e.stderr}")
                return "error"
            except Exception as e:
                print_error(f"Unexpected error: {str(e)}")
                return "error"
            return "success"
