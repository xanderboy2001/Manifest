#!/usr/bin/env python3
"""Execute the primary command-line interface for the Manifest dotfile manager.

This module serves as the entry point for the application, handling argument
parsing, configuration loading, and the orchestration of the interactive
terminal UI menus for managing GNU Stow configurations.

"""

import argparse
import sys
from pathlib import Path

from manifest.core.config import ConfigManager
from manifest.core.git import GitManager
from manifest.core.stow import StowManager
from manifest.core.ui import UIManager
from manifest.core.utils import (
    ask_to_return,
    print_debug,
    print_error,
    print_menu_output,
    print_success,
    print_warning,
    set_log_level,
    setup_utils_theme,
)


def handle_stow_menu(
    stow_manager: StowManager, ui_manager: UIManager, git_manager: GitManager | None
) -> bool:
    """Execute functions selected from the stow management sub-menu.

    Provides a loop that captures user input from the UI and dispatches the
    appropriate StowManager actions, such as listing or adding configurations.

    Args:
        stow_manager (StowManager): The manager instance handling Stow logic.
        ui_manager (UIManager): The UI instance handling user interaction and menus.
        git_manager (GitManager): An optional GitManager instance. If provided, changes
            are committed to the repository after each successful operation.

    Returns:
        bool: True if the user chooses to return to the previous menu.

    """
    while True:
        selected = ui_manager.stow_menu()
        match selected:
            case "list_configs":
                configs = stow_manager.list_configs()
                print_menu_output(configs, title="Configs")
            case "add_config":
                config_path = ui_manager.get_path(
                    message="Path to configuration files (/home/user/.config/program)",
                    starting_dir="~",
                )
                output = stow_manager.add_config(Path(config_path))
                if output == "error":
                    ask_to_return()
                else:
                    print_success(f"Successfully added {config_path} to Manifest!")

                if git_manager:
                    pkg_name = Path(config_path).stem
                    default_msg = f"Add {pkg_name} config"

                    git_manager.stage_config(pkg_name)

                    commit_msg = ui_manager.get_commit_message(default=default_msg)
                    git_manager.commit(commit_msg)
                else:
                    print_debug("No git_manager")
            case "remove_config":
                config_name = ui_manager.choose_config(
                    configs=stow_manager.list_configs(),
                    prompt="Choose a config to remove from Manifest",
                )
                while config_name is None:
                    print_error("Please select a config")
                    config_name = ui_manager.choose_config(
                        configs=stow_manager.list_configs(),
                        prompt="Choose a config to remove from Manifest",
                    )
                output = stow_manager.remove_config(config_name)
                if output == "error":
                    ask_to_return()
                else:
                    print_success(f"Successfully removed {config_name} from Manifest!")

                if git_manager:
                    pkg_name = Path(config_name).stem
                    default_msg = f"Remove {pkg_name} config"

                    git_manager.stage_config(config_name)

                    commit_msg = ui_manager.get_commit_message(default=default_msg)
                    git_manager.commit(commit_msg)
            case "remove_all_configs":
                if ui_manager.confirm_destructive_action("remove all configs"):
                    stow_manager.remove_all_configs()
                    print_success(
                        "Successfully removed all configurations from Manifest"
                    )
                else:
                    print_warning("User cancelled removal")
            case "deploy_config":
                config_name = ui_manager.choose_config(
                    configs=stow_manager.list_configs(),
                    prompt="Choose a config to deploy",
                )
                while config_name is None:
                    print_error("Please select a config")
                    config_name = ui_manager.choose_config(
                        configs=stow_manager.list_configs(),
                        prompt="Choose a config to deploy",
                    )
                output = stow_manager.deploy_config(config_name)
                if output != "error":
                    print_success(f"Successfully deployed {config_name}!")
                ask_to_return()
            case "update_config":
                config_name = ui_manager.choose_config(
                    configs=stow_manager.list_configs(),
                    prompt="Choose a config to redeploy",
                )
                while config_name is None:
                    print_error("Please select a config")
                    config_name = ui_manager.choose_config(
                        configs=stow_manager.list_configs(),
                        prompt="Choose a config to redeploy",
                    )
                output = stow_manager.update_config(config_name)
                if output != "error":
                    print_success(f"Successfully updated {config_name}!")
                ask_to_return()
            case "back" | None:
                return True
            case _:
                print_error(f"Unknown function in stow menu: {selected}")


def handle_settings_menu(config_manager: ConfigManager, ui_manger: UIManager) -> bool:
    """Run functions from the settings menu based on user selection.

    Provides a loop that captures user input from the settings sub-menu and
    dispatches corresponding configuration tasks such as viewing, editing,
    importing, or exporting application settings.

    Args:
        config_manager (ConfigManager): The configuration manager instance for handling
            settings persistence and configuration parsing.
        ui_manger (UIManager): The UI instance handling user interaction
            and settings menus.

    Returns:
        bool: True if the user chooses to return to the previous menu.

    """
    while True:
        selected = ui_manger.settings_menu()
        match selected:
            case "view_settings":
                ui_manger.print_settings_table(config_manager.get_all_opts())
            case "edit_settings":
                setting_to_edit = ui_manger.choose_option_to_edit(
                    config_manager.get_all_opts()
                )
                if not setting_to_edit:
                    return True
                if setting_to_edit == "back":
                    return True
                default = None
                if config_manager.get_opt(setting_to_edit):
                    default = config_manager.get_opt(setting_to_edit)
                new_value = ui_manger.edit_setting(default)
                config_manager.set_opt(key=setting_to_edit, value=new_value)
            case "import_settings":
                pass
            case "export_settings":
                pass
            case "reset_settings":
                pass
            case "back" | None:
                return True
            case _:
                print_error(f"Unknown function in settings menu: {selected}")
        ask_to_return()


def handle_git_menu(ui_manager: UIManager, git_manager: GitManager | None) -> bool:
    """Handle the main loop and routing for the interactive Git menu.

    Displays the Git menu, processes the user's selection, and calls the
    appropriate methods on the GitManager and UIManager to execute commands
    like staging, committing, and viewing status.

    Args:
        ui_manager (UIManager): The user interface manager responsible for
            displaying menus, tables, and prompting for inputs.
        git_manager (GitManager | None): The manager responsible for executing
            actual Git commands. If None, it indicates Git is not enabled.

    Returns:
        bool: Always returns True when the user chooses to go back or if
        Git is not enabled, indicating control should be returned to the parent menu.

    """
    if not git_manager:
        print_error("Git is not enabled!")
        return True
    while True:
        ahead, behind = git_manager.get_sync_status()
        enable_push = False
        enable_pull = False
        if ahead > 0:
            enable_push = True
        if behind > 0:
            enable_pull = True
        selected = ui_manager.git_menu(allow_push=enable_push, allow_pull=enable_pull)
        match selected:
            case "stage":
                git_manager.stage_all()
                ask_to_return()
            case "commit":
                git_manager.commit(ui_manager.get_commit_message(""))
                ask_to_return()
            case "push":
                git_manager.push()
                ask_to_return()
            case "pull":
                git_manager.pull()
                ask_to_return()
            case "status":
                status = git_manager.get_status()
                ui_manager.print_git_status_table(status)
                ask_to_return()
            case "back" | None:
                return True
            case _:
                print_error(f"Unknown function in git menu: {selected}")


def first_run(ui: UIManager, cfg: ConfigManager, manifest_path: str):
    """Run the initial setup wizard on the first launch of the application.

    Guides the user through configuring the manifest path, enabling Git,
    and optionally connecting to a remote repository. Persists all choices
    to the configuration manager. Exits early at any step if the user
    declines further setup.

    Args:
        ui (UIManager): The UI instance used to prompt the user through
            each setup step.
        cfg (ConfigManager): The configuration manager used to persist
            settings selected during setup.
        manifest_path (str): The default manifest path to suggest to the
            user, sourced from CLI arguments or application defaults.

    """
    final_path = ui.set_manifest_path(manifest_path)

    if final_path != manifest_path:
        cfg.set_opt("manifest_path", final_path)
        manifest_path = final_path

    if not ui.prompt_for_git():
        cfg.set_opt(key="use_git", value="False")
        return

    cfg.set_opt("use_git", "True")

    if not ui.prompt_for_remote():
        # No remote - just init locally, nothing else needed
        git_manager = GitManager(manifest_path=manifest_path)
        git_manager.init_repo()
        return

    cfg.set_opt("use_remote", "True")

    platform = ui.prompt_for_remote_platform()
    cfg.set_opt("remote_platform", platform)

    git_manager = GitManager(manifest_path=manifest_path)
    auth_method = git_manager.detect_auth_method()
    cfg.set_opt("remote_auth_method", auth_method)

    if auth_method == "pat":
        cfg.set_opt("remote_pat", ui.prompt_for_pat())

    choice = ui.prompt_create_or_use_existing()

    if choice == "create":
        git_manager.init_repo()
        if auth_method != "gh_cli":
            print_warning("Remote repository creation requires GitHub CLI")
            remote_url = ui.prompt_for_remote_url()
        else:
            repo_name = ui.prompt_for_repo_name(default=Path(manifest_path).stem)
            remote_url = git_manager.create_github_repo(repo_name)
            if not remote_url:
                print_error("Failed to create GitHub repository. Aborting setup.")
                return

        if auth_method == "ssh":
            remote_url = git_manager._to_ssh_url(remote_url)
        elif auth_method == "gh_cli":
            if git_manager._get_gh_protocol() == "ssh":
                remote_url = git_manager._to_ssh_url(remote_url)
        cfg.set_opt("remote_url", remote_url)
        git_manager.stage_all()
        git_manager.add_remote(remote_url)
        git_manager.commit("Initial commit", allow_empty=True)
        git_manager.push(set_upstream=True)

    else:  # "existing"
        if auth_method == "gh_cli":
            selected_repo = ui.select_gh_repo(git_manager.get_gh_repos())
            if not selected_repo:
                print_error(
                    "Failed to get selection for existing GitHub repository. "
                    + "Aborting setup."
                )
                return
            git_manager.clone_repo(repo=selected_repo, use_ghcli=True)
        else:
            remote_url = ui.prompt_for_remote_url()
            if auth_method == "ssh":
                remote_url = git_manager._to_ssh_url(remote_url)
            cfg.set_opt("remote_url", remote_url)
            git_manager.add_remote(remote_url)
            git_manager.stage_all()
            git_manager.commit("Initial commit", allow_empty=True)
            git_manager.push(set_upstream=True)


def main():
    """Initialize the application and run the main event loop.

    Parses command-line arguments, sets up the configuration and UI themes,
    ensures the manifest directory exists, and manages the top-level navigation
    between different application modules.

    """
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
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose debug output"
    )
    args = parser.parse_args()
    set_log_level(args.verbose)

    cfg = ConfigManager()

    rich_theme = cfg.get_rich_style()
    setup_utils_theme(rich_theme)

    ui = UIManager(rich_theme=rich_theme)

    # Initial Path Logic
    manifest_path = args.path or cfg.get_opt("manifest_path") or "."
    if cfg.first_run:
        first_run(ui=ui, cfg=cfg, manifest_path=manifest_path)

    if cfg.get_opt("use_git") == "True":
        git_manager = GitManager(manifest_path=manifest_path)
    else:
        git_manager = None

    stow = StowManager(manifest_path)
    stow.ensure_manifest_dir()

    while True:
        main_menu_function = ui.main_menu()
        print_debug(main_menu_function or "")
        match main_menu_function:
            case "stow":
                handle_stow_menu(
                    stow_manager=stow, ui_manager=ui, git_manager=git_manager
                )
            case "settings":
                handle_settings_menu(config_manager=cfg, ui_manger=ui)
            case "git":
                handle_git_menu(ui_manager=ui, git_manager=git_manager)
            case "exit" | None:
                print_debug("Goodbye!")
                sys.exit(0)


if __name__ == "__main__":
    main()
