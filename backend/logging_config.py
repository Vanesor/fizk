from loguru import logger
import sys

logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level: <8}</level> | <cyan>{message}</cyan>",
    level="INFO",
)

import logging
for name in ("uvicorn.access", "uvicorn.error"):
    logging.getLogger(name).handlers.clear()
    logging.getLogger(name).addHandler(logger._core.handlers[0])
