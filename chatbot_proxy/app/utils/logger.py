import sys
from loguru import logger


def setup_logger():
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{extra[request_id]}</cyan> | <level>{message}</level>",
        level="DEBUG",
    )
    logger.add(
        "data/logs.log",
        rotation="10 MB",
        format="{time} | {level} | {extra[request_id]} | {message}",
        level="INFO",
    )


def get_logger(request_id: str = "system"):
    return logger.bind(request_id=request_id)
