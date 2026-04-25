from datetime import datetime

from loguru import logger


def setup_logger(app):
    logger.add("logs/file.log", rotation="50 MB")
    logger.info(f"logs initialized {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
