import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import allure
from common.assert_util import assert_with_log
import logging

log=logging.getLogger(__name__)

@allure.epic("小牛电商")
@allure.feature("登录模块-ui")
class TestLoginUi():

    @pytest.mark.ui
    @pytest.mark.login_ui
    def test_login_ui(self,driver,URL):
        driver.get(URL)

        with allure.step("定位账号、密码输入框和登录按钮"):
            login_elem=driver.find_element(By.ID,'username')
            password_elem=driver.find_element(By.XPATH,'//*[@id="password"]')
            login_botton=driver.find_element(By.ID,'loginBtn')
        

        assert_with_log(login_botton.is_displayed(),"登录按钮不可见")
        assert_with_log(login_botton.text=='登录', f"登录按钮文本异常,预期文本: 登录,实际文本: {login_botton.text}")
        assert_with_log(login_botton.is_enabled,"登录按钮不可见")

        with allure.step("清空输入框"):
            login_elem.clear()
            password_elem.clear()

        with allure.step(f"输入账号:tester,密码:123456,点击登录"):
            login_elem.send_keys('tester')
            password_elem.send_keys('123456')
            login_botton.click()

        WebDriverWait(driver=driver,timeout=5).until(
            EC.visibility_of_element_located(By.ID,'toast'))
        toast=driver.find_element(By.ID,'toast')
        assert_with_log(toast.text=='登陆成功',"登录toast异常")

        token=driver.execute_script("return localStorage.getItem('practice_token);")
        assert_with_log(bool(token),"登陆后,token未存入本地")

        time.sleep(2)


