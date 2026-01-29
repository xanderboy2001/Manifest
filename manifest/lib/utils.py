import logging

from rich.logging import RichHandler

logging.basicConfig(
    level="DEBUG",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)],
)

logger = logging.getLogger("rich")


def print_error(message: str) -> None:
    logger.error(message)


def print_debug(message: str) -> None:
    logger.debug(message)
