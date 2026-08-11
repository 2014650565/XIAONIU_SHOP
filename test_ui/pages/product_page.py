from selenium import webdriver
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

    def _product_card(self,name):
        locator=(By.XPATH, f"//article[contains(@class,'product-card')][.//h3[contains(text(),'{name}')]]")
        return self.find(locator)


    def get_product_name(self,name):
        cart=self._product_card(name)
        return cart.find_element(*self.PRODUCT_NAME).text

    def get_product_desciption(self,name):
        return self._product_card(name).find_element(*self.PRODUCT_DESC).text

    def get_product_price(self,name):
        return self._product_card(name).find_element(*self.PRICE).text

    def get_product_stock(self,name):
        return self._product_card(name).find_element(*self.STOCK).text

    def get_add_cart_button_text(self,name):
        return self._product_card(name).find_element(*self.ADD_CART_BTN).text

    def click_add_to_cart_button(self,name):
        self._product_card(name).find_element(*self.ADD_CART_BTN).click()

    def add_to_cart_button_is_enable(self,name):
        return self._product_card(name).find_element(*self.ADD_CART_BTN).is_enabled()


    def get_refresh_button_is_enable(self):
        return self.find(self.REFRESH_BUTTON).is_enabled()
    def get_refresh_button_text(self):
        return self.find(self.REFRESH_BUTTON).text
    def click_refresh_button(self):
        self.find(self.REFRESH_BUTTON).click()