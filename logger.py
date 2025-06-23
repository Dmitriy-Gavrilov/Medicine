import logging
from logging.handlers import TimedRotatingFileHandler
import os


class AppLogger:

    def __init__(
            self,
            name: str = "api_logger",
            log_level: str = "INFO",
            log_dir: str = "logs",
            log_file: str = "api.log",
            backup_count: int = 30,
            console_logging: bool = False,
    ):
        self.name = name
        self.log_level = log_level
        self.log_dir = log_dir
        self.log_file = log_file
        self.backup_count = backup_count
        self.console_logging = console_logging
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        os.makedirs(self.log_dir, exist_ok=True)

        logger = logging.getLogger(self.name)
        logger.setLevel(self.log_level)

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )

        file_handler = TimedRotatingFileHandler(
            filename=os.path.join(self.log_dir, self.log_file),
            when="midnight",
            interval=1,
            backupCount=self.backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        if self.console_logging:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        return logger

    def get_logger(self) -> logging.Logger:
        return self.logger


logger = AppLogger().get_logger()