import os
import sys
import time

from datetime import datetime

import selenium.webdriver
import loguru
from loguru import logger

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

from app.sender import sent_message_into_queue
from driver import create_driver
from twocaptcha import TwoCaptcha


def consul_handler():
    driver = create_driver()
    link = os.getenv("CONSUL_LINK", "")
    driver.get(link)
    actions = ActionChains(driver)
    wait = WebDriverWait(driver, 10)

    # solve capture
    img = driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_imgSecNum"]')
    actions.move_to_element(img)
    actions.perform()
    # driver.save_screenshot("./screens/0.png")
    captcha_path = get_captcha(img)
    solved_captcha = get_solved_captcha(captcha_path)
    logger.info(f"Captcha image:{captcha_path}. Captcha solve: {solved_captcha}")

    captcha_response = driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_txtCode"]')
    captcha_response.send_keys(solved_captcha)
    actions.move_to_element(captcha_response)
    actions.perform()
    # driver.save_screenshot("./screens/1.png")
    captcha_response.send_keys(selenium.webdriver.Keys.ENTER)
    time.sleep(10)
    footer = driver.find_element(By.XPATH, '//*[@id="footer"]')
    actions.move_to_element(footer)
    # driver.save_screenshot("./screens/2.png")
    try:
        driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_lblCodeErr"]')
    except NoSuchElementException:
        continue_button = driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_ButtonB"]')
        continue_button.click()
        time.sleep(10)
        driver.save_screenshot(f"./screens/{str(datetime.now().date())}.png")
        sent_message_into_queue(f"Log from consul_reg: {str(datetime.now().date())} | Successed update query")
        logger.info("Successed update query")
    else:
        driver.save_screenshot(f"./screens/wrong_{str(datetime.now().date())}.png")
        sent_message_into_queue(f"Log from consul_reg: {str(datetime.now().date())} | Wrong capture")
        logger.error("Wrong capture")

    driver.close()


def get_captcha(img) -> str:
    # download the image as screenshot
    file_name = f"captcha_{str(datetime.now().date())}.png"
    file_path = os.path.join(os.getenv("CAPTCHA_IMG_PATH", ""), file_name)
    img.screenshot(file_path)
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
