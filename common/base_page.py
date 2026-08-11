from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:

    def __init__(self,driver,timeout:int=5):
        self.driver=driver
        self.wait=WebDriverWait(driver,timeout)

    def open(self,url:str):
        self.driver.get(url)

    def find(self,locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def click(self,locator):
        return self.find(locator).click()

    def input_text(self,locator,text:str):
        el=self.find(locator)
        el.clear()
        el.send_keys(text)

    def get_text(self,locator):
        return self.find(locator).text