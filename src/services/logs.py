from loguru import logger
from datetime import datetime

def setup_logger(app):
    logger.add("logs/file.log", rotation="50 MB")
    logger.info(f"logs initialized {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")