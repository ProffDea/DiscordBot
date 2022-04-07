import datetime
import logging

from src import config

today = datetime.datetime.now()


def create(job):
    to_file = config.get("LOG_TO_FILE")
    to_console = config.get("LOG_TO_CONSOLE")
    if to_file or to_console:
        local_format = get_format()
        file_format = get_file_format()
        level = get_level()
        logger = logging.getLogger(job)
        logger.setLevel(level)
        if to_file:
            file_handler = logging.FileHandler(
                filename="logs/%s_%s.log" % (job, file_format),
                encoding="utf-8",
                mode="w"
            )
            file_handler.setFormatter(local_format)
            logger.addHandler(file_handler)
        if to_console:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(local_format)
            logger.addHandler(stream_handler)


def get_level():
    level = logging.NOTSET
    configs = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]
    lvls = [
        logging.CRITICAL, logging.ERROR, logging.WARNING,
        logging.INFO, logging.DEBUG, logging.NOTSET
    ]
    log_lvl = config.get("LOG_LVL")
    if log_lvl in configs:
        level = lvls[configs.index(log_lvl)]
    return level


def get_format():
    return logging.Formatter(
        "%(asctime)s:%(levelname)s:%(name)s: %(message)s"
    )


def get_file_format():
    return "%s-%s-%s_%s-%s-%s" % (
        today.year, today.month, today.day,
        today.hour, today.minute, today.second
    )
