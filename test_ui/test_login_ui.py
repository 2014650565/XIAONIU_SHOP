import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import allure
from common.assert_util import assert_with_log
import logging
from test_ui.pages.login_page import LoginPage
from common.csv_util import csv_load

log=logging.getLogger(__name__)

@allure.epic("小牛电商")
@allure.feature("登录模块-ui")
@pytest.mark.ui
@pytest.mark.login_ui
class TestLoginUi():

    @pytest.fixture(autouse=True)
    def init_page(self,driver,URL):
        self.page=LoginPage(driver,URL)


    @allure.story("登录")
    @allure.title("登陆账号: {username},密码: {password}")
    @pytest.mark.parametrize('username,password,expect_success,expect_toast',csv_load(r'test_ui\data\login.csv'))
    def test_login_ui(self,username,password,expect_success,expect_toast):

        with allure.step("打开网页"):
            self.page.open()

        with allure.step("定位账号、密码输入框和登录按钮"):
            login_elem=self.page.find(self.page.USERNAME)
            password_elem=self.page.find(self.page.PASSWORD)
            login_button=self.page.find(self.page.LOGINBTN)
        

        assert_with_log(login_button.is_displayed(),"登录按钮不可见")
        assert_with_log(login_button.text=='登录', f"登录按钮文本异常,预期文本: 登录,实际文本: {login_button.text}")
        assert_with_log(login_button.is_enabled(),"登录按钮不可用")

        # with allure.step("清空输入框"):
            # login_elem.clear()
            # password_elem.clear()

        with allure.step(f"输入账号:{username},密码:{password},点击登录"):
            self.page.input_username(username)
            self.page.input_password(password)
            self.page.loginbtn_click()

        toast=self.page.wait.until(
            EC.visibility_of_element_located(self.page.TOAST))
        assert_with_log(toast.text==expect_toast,"登录toast异常")

        expect_success = expect_success.strip().upper() == 'TRUE'
        token=self.page.driver.execute_script("return localStorage.getItem('practice_token');")
        assert_with_log(bool(token)==expect_success,"登录token出现异常")

        # self.page.click(self.page.LOGOUTBTN)


