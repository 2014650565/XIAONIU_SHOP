from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class BasePage:
    TOAST=(By.ID,'toast')

    def __init__(self,driver,timeout:int=20):
        self.driver=driver
        self.wait=WebDriverWait(driver,timeout)

    def open(self,url:str):
        self.driver.get(url)

    def find(self,locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def click(self,locator):
        el=self.find(locator)
        self.driver.execute_script("arguments[0].click();", el)

    def input_text(self,locator,text:str):
        el=self.find(locator)
        el.clear()
        el.send_keys(text)

    def get_text(self,locator):
        return self.find(locator).text

    def get_toast(self):
         return self.find(self.TOAST).text

    def wait_toast_invisible(self,expect_toast):
            self.wait.until(EC.text_to_be_present_in_element(self.TOAST,expect_toast),
                                                message=f"等待toast出现'{expect_toast}'超时")
            self.wait.until(EC.invisibility_of_element(self.TOAST),
                                                message="等待toast消失超时")
