import logging
import sys
from contextvars import ContextVar

logger_metadata_ctx: ContextVar[dict] = ContextVar("logger_metadata", default={})


class StructuredFormatter(logging.Formatter):

    def format(self, record: logging.LogRecord) -> str:
        metadata: dict = logger_metadata_ctx.get({})
        prefix: str = " ".join([f"[{key}={value}]" for key, value in metadata.items()])
        original: str = super().format(record)
        return f"{prefix} {original}" if prefix else original


def create_logger() -> logging.Logger:
    _logger = logging.getLogger("dropbox_app")
    _logger.setLevel(logging.INFO)  # Set minimum logging level
    handler = logging.StreamHandler(sys.stdout)  # Output logs to stdout
    handler.setFormatter(StructuredFormatter(fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    _logger.addHandler(handler)
    _logger.propagate = False  # Prevent logs from being propagated to the root logger
    return _logger


logger: logging.Logger = create_logger()


def add_logger_metadata(metadata: dict) -> None:
    current = logger_metadata_ctx.get({})
    current.update(metadata)
    logger_metadata_ctx.set(current)
