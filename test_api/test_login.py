import requests
import pytest
import logging
import allure
from common.csv_util import csv_load
from common.assert_util import assert_with_log
from conftest import InitApiClient

log=logging.getLogger(__name__)

@pytest.mark.api
@pytest.mark.login
@allure.epic("小牛电商")
@allure.feature("登录模块-api")
class TestLogin(InitApiClient):


    @allure.story("登录")
    @allure.title("登录,username: {username}, 密码: {password}")
    @pytest.mark.smoke
    @pytest.mark.parametrize('username,password,expected_code',csv_load(r"test_api\data\login_data.csv"))
    def test_login(self,username,password,expected_code):
        with allure.step("发送登录请求:"):
            log.info(f"发送账号:{username} 密码:{password} 预期响应码:{expected_code}")
            resp=self.api_client.post(path='login',json={'username':username,'password':password})

        actual_code=resp.json()['code']
        # if actual_code != int(expected_code):
        #     log.error(f"登录请求失败,登陆账号: {username}, 密码: {password}, 期望code: {expected_code}, 实际code: {actual_code}, 响应信息: {resp.json()['message']}")            
        # assert actual_code == int(expected_code)
        assert_with_log(actual_code == int(expected_code),f"登录请求失败,登陆账号: {username}, 密码: {password}, 期望code: {expected_code}, 实际code: {actual_code}, 响应信息: {resp.json()['message']}")
