import __main__
import os
import datetime
import logging

def start():
    logging.basicConfig(level=logging.INFO)
    
    today = datetime.datetime.now()
    format = "%s-%s-%s:%s-%s-%s" % (today.year, today.month, today.day,
                                    today.hour, today.minute, today.second)
    logger = logging.getLogger("discord")
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename="logs/%s.log" % (format),
                                encoding="utf-8",
                                mode="w")
    handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
    logger.addHandler(handler)