import os

from loguru import logger
from handlers import consul_handler

LOG_PATH = os.environ.get("LOG_PATH")


if __name__ == '__main__':
    try:
        logger.add(LOG_PATH)
        consul_handler()
    except Exception as e:
        logger.exception(e)
