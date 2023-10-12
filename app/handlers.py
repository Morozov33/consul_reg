import os
import sys

import requests
from datetime import datetime
from loguru import logger

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from driver import create_driver
from twocaptcha import TwoCaptcha



def consul_handler():
    driver = create_driver()
    link = os.getenv("CONSUL_LINK", "")
    driver.get(link)
    wait = WebDriverWait(driver, 10)

    # solve capture
    img = driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_imgSecNum"]')
    src = img.get_attribute('src')
    captcha_path = get_captcha(src)
    solved_captcha = get_solved_captcha(captcha_path)
    logger.info(f"Captcha image:{captcha_path}. Captcha solve: {solved_captcha}")

    driver.close()


def get_captcha(src: str) -> str:
    # download the image
    request_image = requests.get(src, stream=True)
    if request_image.status_code == 200:
        file_name = f"captcha_{str(datetime.now().date())}.jpg"
        file_path = os.path.join(os.getenv("CAPTCHA_IMG_PATH", ""), file_name)
        with open(file_path, "wb") as f:
            for chunk in request_image:
                f.write(chunk)

        return file_path


def get_solved_captcha(captcha_path: str) -> int:
    api_key = os.getenv("CAPTCHA_API_KEY")
    solver = TwoCaptcha(api_key)
    try:
        result = solver.normal(captcha_path)
    except Exception as e:
        logger.exception(e)
        sys.exit(e)
    else:
        return int(result.get("code"))
