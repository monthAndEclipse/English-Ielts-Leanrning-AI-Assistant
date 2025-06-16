# app/core/logger.py
import logging
def get_logger(name):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s",
    )
    logger = logging.getLogger(name)
    return logger