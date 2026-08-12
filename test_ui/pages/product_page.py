import re

from selenium.webdriver.common.by import By
from common.base_page import BasePage


class ProductPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

    PRODUCT_NAME = (By.XPATH, ".//h3")
    PRODUCT_DESC = (By.XPATH, ".//p")
    PRICE = (By.XPATH, ".//div[contains(@class,'price')]")
    STOCK = (By.XPATH, ".//div[contains(@class,'stock')]")
    ADD_CART_BTN = (By.XPATH, ".//button[@data-add-cart]")
    REFRESH_BUTTON=(By.ID,'refreshProducts')
    PRODUCT_COUNT=(By.ID,'productCount')

    def _product_card(self,name):
        locator=(By.XPATH, f"//article[contains(@class,'product-card')][.//h3[contains(text(),'{name}')]]")
        return self.find(locator)


    def get_product_name(self,name):
        cart=self._product_card(name)
        return cart.find_element(*self.PRODUCT_NAME).text

    def get_product_desciption(self,name):
        return self._product_card(name).find_element(*self.PRODUCT_DESC).text

    def get_product_price(self,name):
        return self._product_card(name).find_element(*self.PRICE).text[1:]

    def get_product_price_value(self, name):
        # 页面上价格形如 ¥199.00，这里去掉 ¥ 转成数值 199.0
        return float(self.get_product_price(name).replace("¥", "").strip())

    def is_product_price_two_decimals(self, name):
        # 断言商品价格保留两位小数，即 ¥ 后必须正好是 数字.两位小数
        text = self.get_product_price(name).strip()
        return re.fullmatch(r"¥\d+\.\d{2}", text) is not None

    def get_product_stock(self,name):
        return self._product_card(name).find_element(*self.STOCK).text[3:]

    def get_add_cart_button_text(self,name):
        return self._product_card(name).find_element(*self.ADD_CART_BTN).text

    def click_add_to_cart_button(self,name):
        self._product_card(name).find_element(*self.ADD_CART_BTN).click()

    def add_to_cart_button_is_enable(self,name):
        return self._product_card(name).find_element(*self.ADD_CART_BTN).is_enabled()

    def get_product_count_text(self):
        return int(self.find(self.PRODUCT_COUNT).text)

    def get_product_count(self):
        cards = self.driver.find_elements(By.XPATH, "//article[contains(@class,'product-card')]")
        return len(cards)


    def get_refresh_button_is_enable(self):
        return self.find(self.REFRESH_BUTTON).is_enabled()
    def get_refresh_button_text(self):
        return self.find(self.REFRESH_BUTTON).text
    def click_refresh_button(self):
        self.find(self.REFRESH_BUTTON).click()
