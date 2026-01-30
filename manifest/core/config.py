"""Manage application configuration and UI color themes.

This module provides the ConfigManager class for handling persistent user
settings and defines the color palettes used by the UI for consistent
styling across different terminal environments.

Attributes:
    THEMES (dict): A collection of color schemes including "dracula" and "ansi".

"""

from pathlib import Path

THEMES = {
    "dracula": {
        "primary": "#ff79c6",  # Pink (Focus/Hotkeys)
        "secondary": "#bd93f9",  # Purple (Titles)
        "success": "#50fa7b",  # Green
        "warning": "#ffb86c",  # Orange
        "error": "#ff5555",  # Red
        "muted": "#6272a4",  # Comment/Grey
        "border": "#44475a",  # Current Line (Subtle)
    },
    "ansi": {
        "primary": "magenta",
        "secondary": "cyan",
        "success": "green",
        "warning": "yellow",
        "error": "red",
        "muted": "bright_black",
        "border": "white",
    },
}


class ConfigManager:
    """Handle application configuration persistence and default settings.

    This class manages the lifecycle of the user's configuration file, ensuring
    defaults are applied on first run and providing methods to retrieve or
    modify specific configuration options.

    Attributes:
        first_run (bool): Indicates if the user configuration was just created.
        project_root (Path): The root directory of the application source.
        default_file (Path): Path to the template configuration file.
        user_config_path (Path): Path to the active user-specific configuration.
        defaults (dict): Key-value pairs parsed from the default configuration.

    """

    def __init__(self, config_name="manifest.conf") -> None:
        """Initialize the ConfigManager and prepare user configuration.

        Args:
            config_name (str): The filename for the user configuration.
                Defaults to "manifest.conf".

        """
        self.first_run = False
        self.project_root = Path(__file__).parent.parent
        self.default_file = self.project_root / "default.conf"

        # config_dir = Path(
        # os.getenv("XDG_CONFIG_HOME", Path.home() / "config")
        # ) / "manifest"
        config_dir = self.project_root / "config" / "manifest"
        self.user_config_path = config_dir / config_name

        self.defaults = self._parse_file(self.default_file)

        self._ensure_user_config()

    def _parse_file(self, path):
        """Parse key=value files while ignoring comments and whitespace.

        Args:
            path (Path): The filesystem path to the configuration file.

        Returns:
            dict: A dictionary of configuration keys and their associated values.

        """
        options = {}
        if not path.exists():
            return options

        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    options[key.strip()] = val.strip()
        return options

    def _ensure_user_config(self) -> None:
        """Clone default settings to the user's config directory if missing.

        Creates the necessary directory structure and populates a new configuration
        file with default values, setting the `first_run` flag to True.

        """
        if not self.user_config_path.exists():
            self.first_run = True
            self.user_config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.user_config_path, "w") as f:
                for key, value in self.defaults.items():
                    f.write(f"{key}={value}\n")

    def get_all_opts(self) -> dict[str, str]:
        """Retrieve all current user configuration options.

        Parses the user-specific configuration file and returns a dictionary
        containing all defined settings.

        Returns:
            dict[str, str]: A dictionary of configuration keys and their
                associated values.

        """
        return self._parse_file(self.user_config_path)

    def get_opt(self, key: str) -> str | None:
        """Retrieve a specific configuration value by key.

        Checks the user's configuration file first, falling back to application
        defaults if the key is not found.

        Args:
            key (str): The configuration option to retrieve.

        Returns:
            str | None: The value associated with the key, or None if it
                does not exist.

        """
        user_opts = self._parse_file(self.user_config_path)
        return user_opts.get(key, self.defaults.get(key))

    def set_opt(self, key: str, value: str) -> None:
        """Update or add a key-value pair to the user configuration.

        Persists the change immediately by rewriting the user configuration file
        with the updated dictionary of options.

        Args:
            key (str): The configuration key to update.
            value (str): The new value to assign to the key.

        """
        opts = self._parse_file(self.user_config_path)
        opts[key] = value

        with open(self.user_config_path, "w") as f:
            for k, v in opts.items():
                f.write(f"{k}={v}\n")
