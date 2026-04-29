import logging

LOGGER_NAME = "tastewise"


def configure_logging() -> None:
    """Configure stderr progress logging for CLI runs."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )


def get_logger() -> logging.Logger:
    """Return the project logger."""

    return logging.getLogger(LOGGER_NAME)
