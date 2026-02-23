"""Custom logging utilities with colorized console output."""

import logging


class CustomFormatter(logging.Formatter):
    LOG_LEVEL = "[%(levelname)s]"
    FORMAT = " %(asctime)s [%(filename)s:%(lineno)d] " "%(message)s"
    FORMATS = {
        logging.DEBUG: "\033[94m" + LOG_LEVEL + "\033[0m",
        logging.INFO: "\033[92m" + LOG_LEVEL + "\033[0m",
        logging.WARNING: "\033[93m" + LOG_LEVEL + "\033[0m",
        logging.ERROR: "\033[91m" + LOG_LEVEL + "\033[0m",
        logging.CRITICAL: "\033[91m\033[5m" + LOG_LEVEL + "\033[0m",
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno) + self.FORMAT
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def setup_logger(name: str, log_file: str, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(level)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(CustomFormatter())

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
