from pathlib import Path


class ConfigManager:
    def __init__(self, config_name="manifest.conf") -> None:
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
        """Helper to parse key=value files, ignoring comments and whitespace."""
        options = {}
        if not path.exists():
            return options

        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    options[key.strip()] = val.strip()
        return options

    def _ensure_user_config(self) -> None:
        """Clones default.conf to the user's config directory if it doesn't exist."""
        if not self.user_config_path.exists():
            self.user_config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.user_config_path, "w") as f:
                for key, value in self.defaults.items():
                    f.write(f"{key}={value}\n")

    def get_opt(self, key: str) -> str | None:
        """Retrieves a specifiv key."""
        user_opts = self._parse_file(self.user_config_path)
        return user_opts.get(key, self.defaults.get(key))

    def set_opt(self, key: str, value: str) -> None:
        """Updates or adds a key-value pair."""
        opts = self._parse_file(self.user_config_path)
        opts[key] = value

        with open(self.user_config_path, "w") as f:
            for k, v in opts.items():
                f.write(f"{k}={v}\n")
