from selenium import webdriver
from selenium.webdriver.common.by import By
from common.base_page import BasePage



class LoginPage(BasePage):
    def __init__(self,driver,URL):
        self.url=URL
        super().__init__(driver)

    USERNAME=(By.ID,'username')
    PASSWORD=(By.ID,'password')
    LOGINBTN=(By.ID,'loginBtn')
    TOAST=(By.ID,'toast')
    LOGOUTBTN=(By.ID,'logoutBtn')

    def open(self):
        super().open(self.url)

    def input_username(self,username:str='tester'):
        # login_element=self.find(By.ID,'username')
        self.input_text(self.USERNAME,username)

    def input_password(self,password:str='123456'):
        # password_element=self.find(By.ID,'password')
        self.input_text(self.PASSWORD,password)

    def loginbtn_click(self):
        self.click(self.LOGINBTN)

    def login(self,username:str='tester',password:str='123456'):
        self.input_username(username)
        self.input_password(password)
        self.loginbtn_click()