import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from common.base_page import BasePage

class PayPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)