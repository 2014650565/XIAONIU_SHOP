import platform

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest
from selenium.webdriver.common.by import By
from pages.login_page import LoginPage
import logging
import allure

log=logging.getLogger(__name__)

@pytest.fixture(scope='function',autouse=True)
def driver():
    # CI(Linux) 使用无头 Chrome,本地(Windows)继续使用 Edge
    if platform.system() == 'Linux':
        chrome_options = ChromeOptions()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        driver = webdriver.Chrome(options=chrome_options)
    else:
        driver = webdriver.Edge()
        driver.maximize_window()
    driver.implicitly_wait(3)
    yield driver
    driver.quit()

@pytest.fixture(scope='function')
def login(driver,URL):
    page=LoginPage(driver,URL)
    with allure.step("打开网页"):
        page.open()
    with allure.step("登录"):
        username,password='tester','123456'
        page.login(username,password)
        log.info(f"登陆账号: {username},密码: {password}")
    WebDriverWait(driver, 10).until(
    EC.text_to_be_present_in_element(page.TOAST, "登录成功"),
    message="等待登录toast出现超时")
    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located(page.TOAST),
        message="等待登录toast消失超时")

@pytest.fixture(scope='session')
def URL():
    yield "http://ceshixiaoniu.com/ecommerce-practice-app.html"