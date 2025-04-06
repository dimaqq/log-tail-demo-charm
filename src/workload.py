#!/usr/bin/env python3
import logging
from logging.handlers import RotatingFileHandler
import time

def setup_logger(name, log_file, level=logging.INFO):
    logger = logging.getLogger(name)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler = RotatingFileHandler(log_file, maxBytes=100, backupCount=2)
    handler.setFormatter(formatter)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

access_logger = setup_logger("access", "/tmp/access.log")
error_logger = setup_logger("error", "/tmp/error.log", level=logging.ERROR)
audit_logger = setup_logger("audit", "/tmp/audit.log")


def main_loop():
    while True:
        access_logger.info("Access log entry")
        error_logger.error("Error log entry")
        audit_logger.info("Audit log entry")
        time.sleep(1)


if __name__ == "__main__":
    main_loop()
