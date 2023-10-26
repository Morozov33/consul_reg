import os

from loguru import logger
from handlers import consul_handler
from driver import create_driver

LOG_PATH = os.environ.get("LOG_PATH")
LINKS = list(os.getenv("CONSUL_LINKS", "").split(","))
NAMES = list(os.getenv("NAMES", "").split(","))
names_links = {
    NAMES[0]: LINKS[0],
    NAMES[1]: LINKS[1],
}


if __name__ == '__main__':
    try:
        logger.add(LOG_PATH)
        driver = create_driver()
        for name in names_links:
            consul_handler(name, names_links[name], driver)
    except Exception as e:
        logger.exception(e)
    finally:
        driver.close()
