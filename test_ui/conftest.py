from selenium import webdriver
import pytest
from selenium.webdriver.common.by import By

@pytest.fixture(scope='session',autouse=True)
def driver():
    driver=webdriver.Edge()
    driver.implicitly_wait(3)
    driver.maximize_window()
    yield driver
    driver.quit()

@pytest.fixture(scope='function')
def login(driver,URL):
    driver.get(URL)
    driver.find_element(By.ID,'loginBtn').click()

@pytest.fixture(scope='session')
def URL():
    yield "http://ceshixiaoniu.com/ecommerce-practice-app.html"