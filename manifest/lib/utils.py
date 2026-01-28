import sys


class Colors:
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    LIGHT_GRAY = "\033[37m"
    GRAY = "\033[90m"
    LIGHT_RED = "\033[91m"
    LIGHT_GREEN = "\033[92m"
    LIGHT_YELLOW = "\033[93m"
    LIGHT_BLUE = "\033[94m"
    LIGHT_MAGENTA = "\033[95m"
    LIGHT_CYAN = "\033[96m"
    WHITE = "\033[97m"
    END = "\033[0m"
    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALICS = "\033[3m"
    UNDERLINE = "\033[4m"


def print_error(message: str) -> None:
    """Prints a message to stderr in Red."""
    print(f"{Colors.RED}ERROR: {message}{Colors.END}", file=sys.stderr)


def print_debug(message: str) -> None:
    """Prints a debug message if needed."""
    # Logic to check for DEBUG env var can be added here
    print(f"{Colors.GRAY}[DEBUG] {message}{Colors.END}")
