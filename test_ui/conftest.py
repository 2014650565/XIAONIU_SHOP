from selenium import webdriver
import pytest
from selenium.webdriver.common.by import By
from pages.login_page import LoginPage
import logging
import allure

log=logging.getLogger(__name__)

@pytest.fixture(scope='function',autouse=True)
def driver():
    driver=webdriver.Edge()
    driver.implicitly_wait(3)
    driver.maximize_window()
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

@pytest.fixture(scope='session')
def URL():
    yield "http://ceshixiaoniu.com/ecommerce-practice-app.html"