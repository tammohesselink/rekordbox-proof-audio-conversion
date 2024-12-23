import sys

from loguru import logger as _logger

# Remove the default sink (console)
_logger.remove()
_logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    colorize=True,
)

# Explicitly export the logger
logger = _logger

__all__ = ["logger"]
