# Architecture

## Overview

## Data Flow

**Entry point(s):**
The program starts in `main.py` by calling the `main()` function, which
initializes the application and runs the main event loop.

**Core flow:**

1. **Initial Setup:** If it's the first run, the `first_run()` function is
   called to guide through the initial setup process, asking for the
   manifest path, Git usage, and remote hosting details.
2. **Main Loop:** The main event loop continuously displays the main menu using
   the `UIManager` class, prompting the user for their next action
   (e.g., manage configurations, perform Git operations).
3. **Menu Handling:** Depending on the user's selection:
   - If the user selects to handle dotfiles, the `handle_stow_menu()` function
     is called, allowing actions such as listing, adding, removing, deploying,
     and updating configuration packages using the `StowManager` class.
   - If the user selects Git operations, the `handle_git_menu()` function is
     invoked, enabling Git-related actions through the `GitManager` class
     (e.g., initializing a repository, cloning repositories, pushing/pulling changes).
   - For settings management, the `handle_settings_menu()` function provides options
     to view or modify application settings.
4. **Configuration Management:** The `ConfigManager` class handles reading,
   writing, and updating configuration files, ensuring that user preferences are
   persisted across sessions.
5. **Git Integration:** Git operations are managed through methods in the
   `GitManager` class, which interfaces with the system's Git commands via
   subprocesses and provides methods for repository initialization, cloning,
   pushing/pulling changes, and other Git-related tasks.
6. **Stow Operations:** Stow package management is handled by the `StowManager`
   class, which uses GNU Stow to list, add, remove, deploy, and update
   configuration packages.

**Key data structures:**

- **ConfigManager:** A dictionary-like object that stores user configuration
  settings, allowing for retrieval (`get_opt()`) and updating (`set_opt()`) of
  specific options.
- **GitManager:** An object that encapsulates Git operations, managing
  repository initialization, cloning, pushing/pulling changes, and other
  Git-related tasks through methods like `init_repo()`, `clone_repo()`, and `push()`.
- **StowManager:** A class for managing dotfile packages using GNU Stow,
  providing methods to list, add, remove, deploy, and update configuration packages.
- **UIManager:** An object that manages the user interface, displaying menus,
  prompts, and outputs using Rich for colorful console printing.

The data flows through these modules as follows:

1. The `main()` function initializes the application by creating instances of
   `ConfigManager`, `GitManager`, `StowManager`, and `UIManager`.
2. User interactions are handled through the `UIManager`, which invokes
   functions like `handle_stow_menu()`, `handle_git_menu()`, or
   `handle_settings_menu()` based on user input.
3. These functions utilize the `ConfigManager` to retrieve settings, the
   `GitManager` for Git operations, and the `StowManager` for managing dotfiles.
4. The results of these operations are then displayed back through the
   `UIManager`, ensuring a seamless interaction loop between the user and the application.

## Modules

### `main.py`

**Purpose:** This file is the entry point for a dotfile management application
using GNU Stow, providing a command-line interface with menus for managing
configurations, settings, and Git operations.
**Exports:**

- `main`: Initializes the application and runs the main event loop.
- `handle_stow_menu`, `handle_settings_menu`, `handle_git_menu`: Functions to handle
  specific sub-menus.
- `first_run`: Handles the initial setup wizard on first launch.
  **Depends on:**
- Internal project imports from `manifest.core.config`, `manifest.core.git`,
  `manifest.core.stow`, and `manifest.core.ui`.
  **State / Side effects:**
- File I/O for configuration persistence (e.g., reading/writing to config files).
- Network calls if Git is enabled and configured.
- Global state management through configuration settings and UI interactions.
  **Incomplete / Suspicious:**
- The functions `handle_settings_menu` currently have placeholders for
  importing, exporting, and resetting settings. These are not implemented.
- There might be potential improvements in error handling and user
  input validation throughout the code.

### `config.py`

**Purpose:** Manages application configuration and UI color themes, providing
methods for initializing, parsing, and updating user settings.

**Exports:**

- `ConfigManager`: Handles the lifecycle of the user's configuration file,
  ensuring defaults are applied on first run and providing methods to
  retrieve or modify specific configuration options.
  - `_parse_file(path)`: Parses key=value files while ignoring comments and whitespace.
  - `_ensure_user_config()`: Clones default settings to the user's config
    directory if missing.
  - `get_all_opts()`: Retrieves all current user configuration options.
  - `get_opt(key)`: Retrieves a specific configuration value by key.
  - `set_opt(key, value)`: Updates or adds a key-value pair to the user configuration.
  - `get_rich_style()`: Loads and returns a Rich Theme based on the configured
    theme name.

**Depends on:**

- Internal project imports: `pathlib`, `shutil`, `configparser`, `rich.theme`,
  and `utils`.

**State / Side effects:**

- None

**Incomplete / Suspicious:**

- None

### `git.py`

**Purpose:** Provides Git repository integration for a manifest dotfile manager,
automating repository setup and management through subprocess orchestration.

**Exports:**

- `GitManager`: Class that manages Git operations in the manifest directory.
- `_check_git_installed()`: Verifies that Git is installed on the system.
- `_is_initialized()`: Checks if a Git repository already exists at the
  specified path.
- `_check_gh_installed()`: Checks if the GitHub CLI is available.
- `_check_gh_authenticated()`: Verifies that the GitHub CLI has an
  authenticated session.
- `_check_ssh_github()`: Tests SSH authentication to GitHub.
- `_to_ssh_url(url: str) -> str`: Converts a GitHub HTTPS URL to its SSH equivalent.
- `_get_gh_protocol()`: Retrieves the configured Git protocol in the GitHub CLI.
- `init_repo()`: Initializes a new Git repository at the manifest path if it
  doesn't already exist.
- `get_gh_repos()`: Lists all repositories from the authenticated GitHub account.
- `detect_auth_method()`: Determines the best authentication method for GitHub.
- `create_github_repo(repo_name: str, private: bool = True) -> str | None`:
  Creates a new repository on GitHub using the GitHub CLI.
- `clone_repo(repo_name: str, use_ghcli: bool)`: Clones a remote repository
  into the manifest path using either plain git or the GitHub CLI.
- `get_remote_url() -> str`: Retrieves the configured remote origin URL for
  the repository.
- `has_remote() -> bool`: Checks if a remote named 'origin' is configured
  in the local Git repository.
- `add_remote(url: str) -> bool`: Adds or updates the remote origin with the
  specified URL.
- `push(set_upstream: bool = False) -> bool`: Pushes committed changes to the
  remote origin.
- `pull() -> bool`: Pulls the latest changes from the remote origin.
- `get_sync_status() -> tuple[int, int]`: Determines how many commits the
  local branch is ahead or behind the remote.
- `stage_all() -> bool`: Stages all changes in the manifest directory for
  the next commit.
- `stage_config(config_name: str) -> bool`: Stages a specific list of files
  for the next commit.
- `commit(message: str, allow_empty: bool = False) -> bool`: Creates a commit
  with all staged changes.
- `get_status() -> list[tuple[str, str]]`: Returns a list of changed files
  in the repository.

**Depends on:**

- `rich.status.Status` for displaying visual status spinners during operations.
- `manifest.core.utils.*` for utility functions like printing debug, error,
  success, and warning messages.

**State / Side effects:**

- None

**Incomplete / Suspicious:**

- None

### `stow.py`

**Purpose:** Manages dotfiles using GNU Stow, providing functionalities to list,
add, remove, deploy, and update configuration packages.

**Exports:**

- `StowManager`: Class for managing dotfile packages using GNU Stow.
  - `__init__`: Initializes the StowManager with a manifest path.
  - `_check_stow_installed`: Verifies that GNU Stow is installed on the system.
  - `ensure_manifest_dir`: Creates the manifest directory if it does not exist.
  - `list_configs`: Lists subdirectories in the manifest path.
  - `add_config`: Adds existing configuration files to the manifest.
  - `remove_config`: Removes a configuration package from the manifest
    and restores its files.
  - `remove_all_configs`: Removes all configuration packages from the manifest,
    and restores their files.
  - `deploy_config`: Deploys a configuration package from the manifest
    using GNU Stow.
  - `update_config`: Updates an existing configuration package using GNU
    Stow's restow operation.

**Depends on:**

- `shutil`, `subprocess`, `pathlib` for file operations and command execution.
- `rich.status.Status` for status updates.
- `utils.print_debug`, `utils.print_error`, `utils.print_warning` for logging.

**State / Side effects:**

- Performs file I/O (creating directories, moving files) and runs system
  commands (`stow`).

**Incomplete / Suspicious:**

- None

### `ui.py`

**Purpose:** Provides a themed command-line interface for the Manifest dotfile
manager using Rich and Questionary libraries.
**Exports:**

- `UIManager`: Manages terminal user interface interactions and styling.
  - Initializes with a specific color theme.
  - Prints application branding and title panel.
  - Guides through initial setup process, prompting for manifest path,
    Git usage, and remote hosting.
  - Displays interactive menus for main navigation, git management,
    configuration management, and settings management.
  - Prompts for various user inputs such as paths, repository URLs,
    commit messages, etc.
- `print_success`: Prints a success message using the Rich console.
  **Depends on:**
- Internal project imports:
  - `pathlib.Path`
  - `questionary` (for interactive prompts)
  - `rich.console.Console`
  - `rich.panel.Panel`
  - `rich.table.Table`
  - `manifest.core.utils.print_success`
    **State / Side effects:**
- None
  **Incomplete / Suspicious:**
- None

### `utils.py`

**Purpose:** Provides utility functions for CLI output formatting and user
interaction, including standardized logging, colorful console printing
using Rich, and interactive prompts using Questionary.

**Exports:**

- `set_log_level(verbose: bool) -> None`: Set the logging level for the
  application logger.
- `setup_utils_theme(rich_theme: Theme) -> None`: Register the
  application theme with the utility console.
- `print_error(message: str) -> None`: Print an error message to the
  console with a cross symbol.
- `print_warning(message: str) -> None`: Log a warning message using the
  Rich logging handler.
- `print_debug(message: str) -> None`: Log a debug message using the
  Rich logging handler.
- `print_success(message: str) -> None`: Print a success message to the
  console with a checkmark symbol.
- `ask_to_return() -> None`: Prompt the user to press any key to continue.
- `print_menu_output(data: str | list[str], title: str = "Output") -> None`:
  Display data in a styled Dracula-themed panel or table.

**Depends on:**

- `questionary` (third-party library for interactive prompts)
- `rich` (third-party library for colorful console printing and logging)

**State / Side effects:**

- Uses the global Rich console instance for stdout.
- Writes to the application log via the Rich logging handler.
- No file I/O, network calls, or database access.

**Incomplete / Suspicious:**

- The `pal` variable is referenced but not defined within the provided code.
  It should be passed as an argument to functions that use it or imported
  from another module.
- The commented-out sections for styling with the color palette
  (`border_color`, `title_style`) suggest potential future enhancements
  that need to be addressed.

## Known Gaps

- Placeholder code exists in `handle_settings_menu` but is not implemented.

## Missing Pieces

- Implement functionality for importing, exporting, and resetting settings in `handle_settings_menu`.
- Define the `pal` variable referenced in `utils.py`.

## Suggested Next Steps

1. **Implement Settings Management:** Start by implementing the logic for
   importing, exporting, and resetting settings within `main.py`.
   This will involve reading/writing to configuration files.
2. **Resolve `pal` Variable:** Review where `pal` is used (likely in a
   theme-related function) and either define it within the scope
   or import it from another module.
3. **Enhance Error Handling:** Throughout the project, enhance error
   handling and add user input validation to ensure robustness.
4. **Integrate Git Operations:** If Git functionality is intended
   to be fully integrated, consider implementing more comprehensive
   testing for `git.py` functions, especially network-related
   operations if GitHub CLI interaction is enabled.
5. **Test Configuration Persistence:** Ensure that the configuration
   management in `config.py` works as expected and that changes
   persist across application restarts.
