import os
import sys
import time

from datetime import datetime

import selenium.webdriver
from loguru import logger

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, UnexpectedAlertPresentException
from selenium.webdriver.common.action_chains import ActionChains

from sender import sent_message_into_queue
from driver import create_driver
from twocaptcha import TwoCaptcha


def consul_handler(name: str, link: str, driver):

    driver.get(link)
    actions = ActionChains(driver)
    wait = WebDriverWait(driver, 10)

    # solve capture
    img = driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_imgSecNum"]')
    actions.move_to_element(img)
    actions.perform()
    # driver.save_screenshot("./screens/0.png")
    captcha_path = get_captcha(img, name)
    solved_captcha = get_solved_captcha(captcha_path)
    logger.info(f"Captcha image:{captcha_path}. Captcha solve: {solved_captcha} for {name}")

    captcha_response = driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_txtCode"]')
    captcha_response.send_keys(solved_captcha)
    actions.move_to_element(captcha_response)
    actions.perform()
    # driver.save_screenshot("./screens/1.png")
    captcha_response.send_keys(selenium.webdriver.Keys.ENTER)
    time.sleep(5)
    if name.endswith("Antalya"):
        footer = driver.find_element(By.XPATH, '//*[@id="footer"]')
        actions.move_to_element(footer)
        # driver.save_screenshot("./screens/2.png")

    try:
        driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_lblCodeErr"]')
    except NoSuchElementException:
        continue_button = driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_ButtonB"]')
        continue_button.click()
        time.sleep(5)
        driver.save_screenshot(f"./screens/{name}_{str(datetime.now().date())}.png")
        sent_message_into_queue(f"Log from consul_reg: {str(datetime.now().date())} | Successed update query for {name}")
        logger.info(f"Successed update query for {name}")
    except UnexpectedAlertPresentException:
        actions.send_keys(selenium.webdriver.Keys.ENTER)
        actions.perform()
        time.sleep(5)
        continue_button = driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_ButtonB"]')
        continue_button.click()
        time.sleep(5)
        driver.save_screenshot(f"./screens/{name}_{str(datetime.now().date())}.png")
        sent_message_into_queue(
            f"Log from consul_reg: {str(datetime.now().date())} | Successed update query for {name}")
        logger.info(f"Successed update query for {name}")
    else:
        driver.save_screenshot(f"./screens/wrong_{name}_{str(datetime.now().date())}.png")
        sent_message_into_queue(f"Log from consul_reg: {str(datetime.now().date())} | Wrong capture for {name}")
        logger.error(f"Wrong capture for {name}")




def get_captcha(img, name: str) -> str:
    # download the image as screenshot
    file_name = f"captcha_{name}_{str(datetime.now().date())}.png"
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
