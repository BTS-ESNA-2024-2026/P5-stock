from datetime import datetime

from loguru import logger

# Log format kept consistent across stderr and the rotating file. The default
# loguru template hides level padding which makes log lines hard to scan.
LOG_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
    "{name}:{function}:{line} - {message}"
)


def setup_logger(app):
    logger.add(
        "logs/file.log",
        format=LOG_FORMAT,
        rotation="250 MB",
        encoding="utf-8",
        enqueue=True,
        backtrace=False,
        diagnose=False,
    )
    logger.info(f"logs initialized {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
