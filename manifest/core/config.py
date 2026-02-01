"""Manage application configuration and UI color themes.

This module provides the ConfigManager class for handling persistent user
settings and defines the color palettes used by the UI for consistent
styling across different terminal environments.

Attributes:
    THEMES (dict): A collection of color schemes including "dracula" and "ansi".

"""

import shutil
from configparser import ConfigParser
from pathlib import Path

from rich.theme import Theme


class ConfigManager:
    """Handle application configuration persistence and default settings.

    This class manages the lifecycle of the user's configuration file, ensuring
    defaults are applied on first run and providing methods to retrieve or
        parser = configparser.ConfigParser()
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

        Sets up project paths and ensures a user configuration file exists by copying
            defaults if necessary.

        Args:
            config_name (str): The filename for the user configuration.
                Defaults to "manifest.conf".

        """
        self.first_run = False
        self.project_root = Path(__file__).parent.parent
        self.template_dir = self.project_root / "default_configs"
        self.default_file = self.template_dir / "default.conf"

        # config_dir = Path(
        # os.getenv("XDG_CONFIG_HOME", Path.home() / "config")
        # ) / "manifest"
        self.config_dir = self.project_root / "config" / "manifest"
        self.config_file_path = self.config_dir / config_name

        self.theme_dir = self.config_dir / "themes"

        self.config_parser = ConfigParser()

        self.defaults = self._parse_file(self.default_file)
        self._ensure_user_config()

    def _parse_file(self, path: Path) -> dict:
        """Parse key=value files while ignoring comments and whitespace.

        Args:
            path (Path): The filesystem path to the configuration file.

        Returns:
            dict: A dictionary of configuration keys and their associated values.

        """
        options = {}
        if not path.exists():
            return options
        parser = ConfigParser()
        try:
            content = path.read_text()
            if "[" not in content:
                content = f"[DEFAULT]\n{content}"

            parser.read_string(content)

            section = parser.sections()[0] if parser.sections() else "DEFAULT"
            raw_data = dict(parser[section])

            cleaned_data = {}
            for key, value in raw_data.items():
                cleaned_value = value.split(";")[0].strip()
                cleaned_data[key] = cleaned_value
            return cleaned_data
        except Exception as e:
            from .utils import print_error

            print_error(f"Error parsing {path}: {e}")
            return {}

    def _ensure_user_config(self) -> None:
        """Clone default settings to the user's config directory if missing.

        Creates the necessary directory structure and populates a new configuration
        file with default values, setting the `first_run` flag to True.

        """
        config_dir = self.config_file_path.parent

        if not config_dir.exists():
            self.first_run = True
            shutil.copytree(self.template_dir, config_dir, dirs_exist_ok=True)

            temp_default = config_dir / "default.conf"
            if temp_default.exists() and temp_default != self.config_file_path:
                temp_default.rename(self.config_file_path)

    def get_all_opts(self) -> dict | None:
        """Retrieve all current user configuration options.

        Parses the user-specific configuration file and returns a dictionary
        containing all defined settings.

        Returns:
            dict[str, str]: A dictionary of configuration keys and their
                associated values.

        """
        return self._parse_file(self.config_file_path)

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
        user_opts = self._parse_file(self.config_file_path)
        if not user_opts:
            return None
        return user_opts.get(key, self.defaults.get(key))

    def set_opt(self, key: str, value: str) -> None:
        """Update or add a key-value pair to the user configuration.

        Persists the change immediately by rewriting the user configuration file
        with the updated dictionary of options.

        Args:
            key (str): The configuration key to update.
            value (str): The new value to assign to the key.

        """
        opts = self._parse_file(self.config_file_path)
        opts[key] = value

        with open(self.config_file_path, "w") as f:
            for k, v in opts.items():
                f.write(f"{k}={v}\n")

    def get_rich_style(self) -> Theme:
        """Load and return a Rich Theme based on the configured theme name.

        Retrieves the 'theme' option from settings and attempts to load the
        corresponding '.ini' file from the themes directory. Falls back to
        'ansi.ini' if the specified theme is missing.

        Returns:
            A rich.theme Theme object initialized with the styles parsed
            from the theme file.

        """
        theme_name = self.get_opt("theme") or "ansi"
        theme_file = self.theme_dir / f"{theme_name}.ini"
        if not theme_file.exists():
            theme_file = self.theme_dir / "ansi.ini"

        styles = self._parse_file(theme_file)

        return Theme(styles)
