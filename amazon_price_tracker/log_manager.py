import logging.config
from logging import Logger
from pathlib import Path

from amazon_price_tracker.settings import ROOT_DIR


def make_log_dir(dir_path: Path) -> Path:
    log_dir = dir_path / 'logs/'
    log_dir.mkdir(exist_ok=True)
    return log_dir


def load_log_config() -> None:
    log_dir = make_log_dir(ROOT_DIR)

    logging.config.fileConfig(
        fname=str(ROOT_DIR / 'logging.ini'),
        disable_existing_loggers=False,
        defaults={'logdir': log_dir.as_posix()},
    )


def get_logger(name: str = '') -> Logger:
    load_log_config()
    if not name:
        return logging.getLogger()

    return logging.getLogger(name)
