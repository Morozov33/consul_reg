import os

from selenium import webdriver


def create_driver() -> webdriver:
    """
    Инициализирует webdriver - объект для работы с selenium
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--no-zygote')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--headless=new')

    driver= webdriver.Remote(
        command_executor=f"{os.environ.get('SELENIUM_SERVER')}",
        options=options,
    )
    return driver
