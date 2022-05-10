from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import logging

class Session:
    def __init__(self,cookies,uid):
        self.cookies = cookies
        self.uid = uid

def login(username,password):
    logger = logging.getLogger("session")
    cookie_names = [
        "__bpid",
        "acr",
        "bptid",
        "faLayDowCnt",
        "sid"
    ]

    options = Options()
    options.headless = True
    browser = webdriver.Firefox(options=options,executable_path="./geckodriver")
    browser.get("https://www.farmerama.com/")
    current_url = browser.current_url

    username_input = browser.find_element_by_name("username")
    password_input = browser.find_element_by_name("password")
    username_input.send_keys(username)
    password_input.send_keys(password)
    password_input.send_keys(Keys.ENTER)
    WebDriverWait(browser, 15).until(EC.url_changes(current_url))
    try_counter = 0
    while True:
        raw_cookies = browser.get_cookies()
        received_cookie_names = [cookie["name"] for cookie in raw_cookies]

        if all(cookie_name in received_cookie_names for cookie_name in cookie_names) and browser.find_elements_by_class_name("userinfo"):
            break
        elif browser.find_elements_by_class_name("bgcdw_errors_flash"):
            browser.quit()
            logger.error("invalid username or password")
            raise Exception("invalid username or password")
        elif try_counter > 20:
            browser.quit()
            logger.error("failed to get cookies or uid in 20 tries")
            raise Exception("failed to get cookies or uid in 20 tries")
        
        sleep(1)
        try_counter += 1

    uid = browser.find_element_by_class_name("userinfo").text[-8:]
    cookies = {cookie["name"]:cookie["value"] for cookie in raw_cookies if cookie["name"] in cookie_names}
    browser.quit()
    session = Session(cookies,uid)
    logger.info(f"session created for user with uid {session.uid}")
    return session
