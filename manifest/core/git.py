"""Provide Git repository integration for the Manifest dotfile manager.

This module defines the GitManager class, which automates the initialization
and management of a Git-based version control system within the manifest directory.
It ensures environment compatibility by verifying Git installation
and handles repository setup through subprocess orchestration.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path

from rich.status import Status

from manifest.core.utils import print_debug, print_error, print_success, print_warning


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

    def _check_gh_installed(self) -> bool:
        """Check whether the GitHub CLI is available in the system PATH.

        Returns:
            bool: True if 'gh' is found, False otherwise.

        """
        return bool(shutil.which("gh"))

    def _check_gh_authenticated(self) -> bool:
        """Verify that the GitHub CLI has an active authenticated session.

        Runs 'gh auth status' and inspects the return code to determine
        whether the user is currently logged in.

        Returns:
            bool: True if 'gh' reports an authenticated state, False otherwise.

        """
        with Status(
            "Checking authentication status of GitHub CLI...", spinner="dots"
        ) as status:
            try:
                cmd = ["gh", "auth", "status"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                status.update("[bold]Finishing Up...[/]")
                if result.stdout:
                    print_debug(result.stdout)
                return not bool(result.returncode)
            except subprocess.CalledProcessError as e:
                print_error(
                    f"GitHub CLI authentication status verification failed: {e.stderr}"
                )
                return False

    def _check_ssh_github(self) -> bool:
        """Test whether the system can authenticate to GitHub over SSH.

        Attempts a non-login SSH handshake to git@github.com and checks
        the output for GitHub's successful identity acknowledgement string.

        Returns:
            bool: True if SSH authentication succeeds, False otherwise.

        """
        with Status("Testing GitHub connection over SSH...", spinner="dots") as status:
            try:
                cmd = ["ssh", "-T", "git@github.com"]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                status.update("[bold]Finishing Up...[/]")
                if result.stdout:
                    print_debug(result.stdout)
                if result.returncode == 1:
                    return True
                else:
                    return False
            except subprocess.CalledProcessError as e:
                print_error(f"Failed to test connection to GitHub over SSH: {e.stderr}")
                return False

    def _to_ssh_url(self, url: str) -> str:
        """Convert a GitHub HTTPS remote URL to its SSH equivalent.

        Args:
            url (str): A GitHub HTTPS URL in the form
                'https://github.com/owner/repo'

        Returns:
            str: The SSH equivalent in the form 'git@github.com:owner/repo.git'.
                Returns the original URL unchanged if it is not a recognized
                GitHub HTTPS URL.

        """
        if not url.lower().startswith("https://github.com"):
            print_warning(f"{url} is not a recognized GitHub HTTPS URL")
            return url

        owner_repo = url.lower().split("https://github.com/")[1]
        return f"git@github.com:{owner_repo}.git"

    def _get_gh_protocol(self) -> str:
        """Retrieve the Git protocol configured in the GitHub CLI.

        Runs 'gh config get git_protocol' to determine whether the CLI
        is set to communicate over SSH or HTTPS.

        Returns:
            str: Either 'ssh' or 'https'. Defaults to 'https' if the
                command fails or the output is unrecognized.

        """
        with Status(
            "Determining Git Protocol from GitHub CLI...", spinner="dots"
        ) as status:
            try:
                cmd = ["gh", "config", "get", "git_protocol"]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                status.update("[bold]Finishing Up...[/]")
                if result.stdout:
                    if result.stdout.strip() == "ssh":
                        return "ssh"
                    else:
                        print_warning(
                            f"Output: {result.stdout.strip()} not recognized"
                            + "Defaulting to 'https'."
                        )
                        return "https"
                else:
                    print_warning(
                        "Did not receive any output from 'gh config get git_protocol'. "
                        + "Defaulting to 'https'"
                    )
                    return "https"
            except subprocess.CalledProcessError as e:
                print_error(f"Failed to determine GitHub CLI protocol: {e.stderr}")
                return "https"

    def init_repo(self) -> None:
        """Initialize a new Git repository at the manifest path.

        Skips initialization if a repository already exists. Displays a status
        spinner during the operation.

        """
        if self._is_initialized():
            print_debug(
                f"Git repository already initialized at {str(self.manifest_path)}."
            )
            return
        with Status(
            f"Initializing git repository at {str(self.manifest_path)}...",
            spinner="dots",
        ) as status:
            try:
                result = subprocess.run(
                    ["git", "init", str(self.manifest_path)],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                status.update("[bold]Finishing Up...[/]")
                if result.stdout:
                    print_debug(result.stdout)
            except subprocess.CalledProcessError as e:
                print_error(f"Initializing git repository failed: {e.stderr}")

        print_success(f"initialized git repository at {str(self.manifest_path)}")

    def get_gh_repos(self) -> list[str]:
        """Retrieve a list of repository names from the authenticated GitHub account.

        Runs 'gh repo list --json name' and parses the result into a flat list
        of repository name strings.

        Returns:
            list[str]: A list of repository names, or an empty list if the
                request failed or returned no results.

        """
        with Status("Getting list of repos from GitHub...", spinner="dots") as status:
            try:
                cmd = ["gh", "repo", "list", "--json", "name"]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                status.update("[bold]Finishing Up...[/]")
                if result.stdout:
                    repos_data = json.loads(result.stdout)
                    repo_list = [repo["name"] for repo in repos_data]
                    return repo_list
                else:
                    print_error("Could not get any repos from GitHub CLI")
                    return []
            except subprocess.CalledProcessError as e:
                print_error(f"Failed getting repos from GitHub CLI: {e.stderr}")
                return []

    def detect_auth_method(self) -> str:
        """Determine the best available authentication method for GitHub.

        Checks for the GitHub CLI, SSH key access, and falls back to PAT.
        The priority order is: gh_cli > ssh > pat.

        Returns:
            str: One of 'gh_cli', 'ssh', or 'pat'

        """
        if self._check_gh_installed() and self._check_gh_authenticated():
            return "gh_cli"
        if self._check_ssh_github():
            return "ssh"
        return "pat"

    def create_github_repo(self, repo_name: str, private: bool = True) -> str | None:
        """Create a new GitHub repository using the GitHub CLI.

        Requires that 'gh' is installed and authenticated. Runs
        'gh repo create' with the given name and visibility flag.

        Args:
            repo_name (str): The name of the repository to create on GitHub.
            private (bool): Whether the repository should be private.
                Defaults to True.

        Returns:
            str | None: The remote URL of the newly created repository,
                or None if create failed.

        """
        with Status(
            f"Creating repository '{repo_name}' on GitHub...", spinner="dots"
        ) as status:
            try:
                cmd = ["gh", "repo", "create", repo_name]
                if private:
                    cmd.append("--private")
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                status.update("[bold]Finishing Up...[/]")
                if result.stdout:
                    print_debug(result.stdout)
                    print_success(f"Created repository '{repo_name}' on GitHub")
                    return result.stdout.splitlines()[0].strip()
                else:
                    return None
            except subprocess.CalledProcessError as e:
                print_error(f"Failed to create repository on GitHub: {e.stderr}")
                return None

    def clone_repo(self, repo_name: str, use_ghcli: bool) -> None:
        """Clone a remote repository into the manifest path.

        Args:
            repo_name (str): The repository name or URL to clone. When use_ghcli is
                True, this should be a repository name in 'owner/repo' or
                short 'repo' format recognized by the GitHub CLI.
            use_ghcli (bool): If True, clones using 'gh repo clone' instead of
                plain git, which handles authentication automatically.

        """
        if use_ghcli:
            with Status("Cloning Git Repository...", spinner="dots") as status:
                try:
                    cmd = ["gh", "repo", "clone", repo_name, str(self.manifest_path)]
                    subprocess.run(cmd, check=True)
                    status.update("[bold]Finishing Up...[/]")
                except subprocess.CalledProcessError as e:
                    print_error(f"Failed to clone GitHub repo: {e.stderr}")
                    return
        print_success(
            f"Cloned GitHub repository '{repo_name}' to {str(self.manifest_path)}"
        )

    def get_remote_url(self) -> str:
        """Retrieve the configured remote origin URL for the repository.

        Runs 'git config --get remote.origin.url' from the manifest path.

        Returns:
            str: The remote origin URL, or an empty string if no remote is
                configured or the command fails.

        """
        with Status(
            f"Getting Remote URL for Repository at {self.manifest_path}...",
            spinner="dots",
        ) as status:
            try:
                cmd = [
                    "git",
                    "-C",
                    self.manifest_path,
                    "config",
                    "--get",
                    "remote.origin.url",
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                status.update("[bold]Finishing Up...[/]")
                if result.stdout:
                    print_debug(result.stdout)
                    return result.stdout
                else:
                    print_error("Could not get remote url")
                    return ""
            except subprocess.CalledProcessError as e:
                print_error(f"Failed to get remote url: {e.stderr}")
                return ""

    def has_remote(self) -> bool:
        """Check whether the local repository has a configured remote origin.

        Runs 'git remote' and checks for the presence of 'origin'.

        Returns:
            bool: True if a remote named 'origin' exists, False otherwise.

        """
        with Status(
            "Checking whether local repository has a configured remote origin...",
            spinner="dots",
        ) as status:
            try:
                cmd = ["git", "-C", str(self.manifest_path), "remote"]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                status.update("[bold]Finishing Up...[/]")
                if result.stdout:
                    print_debug(result.stdout)
                    if "origin" in result.stdout:
                        return True
                return False
            except subprocess.CalledProcessError as e:
                print_error(
                    "Failed to check whether local repository has a "
                    f"configured remote origin: {e.stderr}"
                )
                return False

    def add_remote(self, url: str) -> bool:
        """Add a remote origin to the local Git repository.

        Runs 'git remote add origin <url>'. If a remote named 'origin'
        already exists, it will be updated via 'git remote set-url' instead.

        Args:
            url (str): The remote repository URL to add.

        Returns:
            bool: True if the remote was added or updated successfully,
                False otherwise.

        """
        if self.has_remote():
            cmd = [
                "git",
                "-C",
                str(self.manifest_path),
                "remote",
                "set-url",
                "origin",
                url,
            ]
        else:
            cmd = ["git", "-C", str(self.manifest_path), "remote", "add", "origin", url]
        with Status(
            "Adding remote origin to the local Git repository...", spinner="dots"
        ) as status:
            try:
                subprocess.run(cmd, check=True)
                status.update("[bold]Finishing Up...[/]")
                print_success("Added remote origin to the local Git repository")
                return True
            except subprocess.CalledProcessError as e:
                print_error(
                    f"Failed to add remote origin to the local git repository: "
                    f"{e.stderr}"
                )
                return False

    def push(self, set_upstream: bool = False) -> bool:
        """Push committed changes to the remote origin.

        Runs 'git push' from the manifest path. On the first push to a new
        remote, passes '--set-upstream origin main' to establish tracking.

        Args:
            set_upstream (bool): If True, sets the upstream tracking branch
                on push. Should be True on the initial push. Defaults to False.

        Returns:
            bool: True if the push succeeded, False otherwise.

        """
        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"

        with Status("Pushing changes to remote origin...", spinner="dots") as status:
            try:
                cmd = ["git", "-C", str(self.manifest_path), "push"]
                if set_upstream:
                    cmd += ["--set-upstream", "origin", "main"]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True,
                    stdin=subprocess.DEVNULL,
                )
                status.update("[bold]Finishing Up...[/]")
                if result.stdout:
                    print_debug(result.stdout)
                print_success("Pushed changed to remote origin")
                return True
            except subprocess.CalledProcessError as e:
                print_error(f"Failed to push to remote origin: {e.stderr}")
                return False

    def pull(self) -> bool:
        """Pull the latest changes from the remote origin.

        Runs 'git pull' from the manifest path using the current tracking
        branch.

        Returns:
            bool: True if the pull succeeded, False otherwise.

        """
        with Status(
            "Pulling changes from the remote origin...", spinner="dots"
        ) as status:
            try:
                cmd = ["git", "-C", str(self.manifest_path), "pull"]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                status.update("[bold]Finishing Up...[/]")
                if result.stdout:
                    print_debug(result.stdout)
                print_success("Pulled changes from remote origin")
                return True
            except subprocess.CalledProcessError as e:
                print_error(f"Failed to pull changes from remote origin: {e.stderr}")
                return False

    def get_sync_status(self) -> tuple[int, int]:
        """Determine how many commits the local branch is ahead or behind remote.

        Runs 'git fetch' followed by 'git rev-list --count' comparisons
        between HEAD and origin/HEAD to calculate divergence.

        Returns:
            tuple[int, int]: A tuple of (commits_ahead, commits_behind).
                Both values will be 0 if the branch is fully in sync or if
                no remote is configured.

        """
        if not self.has_remote():
            return (0, 0)

        with Status("Checking sync status with remote...", spinner="dots") as status:
            try:
                subprocess.run(
                    ["git", "-C", str(self.manifest_path), "fetch"],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                cmd = [
                    "git",
                    "-C",
                    str(self.manifest_path),
                    "rev-list",
                    "--left-right",
                    "--count",
                    "HEAD...@{u}",
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                status.update("[bold]Finishing Up...[/]")

                if result.stdout:
                    ahead, behind = result.stdout.strip().split()
                    return (int(ahead), int(behind))

            except subprocess.CalledProcessError as e:
                print_debug(
                    f"Could not calculate sync status (no upstream branch?): {e.stderr}"
                )
                return (0, 0)
            except ValueError:
                print_error("Failed to parse git rev-list output.")
                return (0, 0)
        return (0, 0)

    def stage_all(self) -> bool:
        """Stage all changes in the manifest directory.

        Runs 'git add -A' from the manifest path to prepare all modified,
        added, and deleted files for the next commit.

        Returns:
            bool: True if staging completed without error, False otherwise.

        """
        with Status("Staging all files for commit...", spinner="dots") as status:
            try:
                cmd = ["git", "-C", str(self.manifest_path), "add", "-A"]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                status.update("[bold]Finishing up...[/]")
                if result.stdout:
                    print_debug(result.stdout)
            except subprocess.CalledProcessError as e:
                print_error(f"Adding unstaged changes failed: {e.stderr}")
                return False
        print_success("Staged all changes")
        return True

    def stage_config(self, config_name: str) -> bool:
        """Stage a specific list of files for the next commit.

        Runs 'git add -- <paths>' from the manifest path to stage only the
        specified files, leaving other changes in the working tree unstaged.

        Args:
            config_name (str): The name of the config to stage.

        Returns:
            bool: True if staging completed without error or if paths was empty,
                False otherwise.

        """
        with Status("Staging files for commit...", spinner="dots") as status:
            try:
                cmd = ["git", "-C", str(self.manifest_path), "add", config_name]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                status.update("[bold]Finishing Up...[/]")
                if result.stdout:
                    print_debug(result.stdout)
            except subprocess.CalledProcessError as e:
                print_error(f"Staging files failed: {e.stderr}")
                return False
        print_success(f"Staged config '{config_name}'")
        return True

    def commit(self, message: str, allow_empty: bool = False) -> bool:
        """Create a commit with all staged changes.

        Args:
            message (str): The commit message describing the change being recorded.
            allow_empty (bool): If True, creates the commit even when there are no
                staged changes. Useful for the initial commit on a new repository.
                Defaults to False.

        Returns:
            bool: True if the commit was created, False otherwise.

        """
        with Status("Committing changes...", spinner="dots") as status:
            try:
                cmd = ["git", "-C", str(self.manifest_path), "commit", "-m", message]
                if allow_empty:
                    cmd.append("--allow-empty")
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                status.update("[bold]Finishing up...[/]")
                if result.stdout:
                    print_debug(result.stdout)
            except subprocess.CalledProcessError as e:
                print_error(f"Committing changes failed: {e.stderr}")
                return False
        print_success("Committed changes")
        return True

    def get_status(self) -> list[tuple[str, str]]:
        """Return a list of changed files in the repository.

        Runs 'git status --short' and translates the status codes into
            human-readable strings.

        Returns:
            list[tuple[str, str]]: A list of tuples containing
                (status_message, file_path), or an empty list if the working tree is
                clean or an error occurred.

        """
        raw_output = ""
        with Status("Getting status of git repository...", spinner="dots") as status:
            try:
                cmd = ["git", "-C", str(self.manifest_path), "status", "--short"]
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
