import __main__
import datetime
import logging

from src import config

def start():
    set_lvl = logging.NOTSET
    configs = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]
    lvls = [logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG, logging.NOTSET]
    log_lvl = config.get("LOG_LVL")
    if log_lvl in configs:
        set_lvl = lvls[configs.index(log_lvl)]

    logging.basicConfig(level=logging.INFO)
    
    today = datetime.datetime.now()
    format = "%s-%s-%s_%s-%s-%s" % (today.year, today.month, today.day,
                                    today.hour, today.minute, today.second)
    logger = logging.getLogger("discord")
    logger.setLevel(set_lvl)
    handler = logging.FileHandler(filename="logs/%s.log" % (format),
                                encoding="utf-8",
                                mode="w")
    handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
    logger.addHandler(handler)