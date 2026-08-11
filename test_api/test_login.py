import requests
import pytest
import logging
import allure
from common.csv_util import csv_load
from common.assert_util import assert_with_log
from common.init_apiclient import InitApiClient

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
    def test_login(self,base_url,username,password,expected_code):
        with allure.step("发送登录请求:"):
            log.info(f"发送账号:{username} 密码:{password} 预期响应码:{expected_code}")
            data=requests.request(method='post',
                                  url=f'{base_url}login',
                                  json={'username':username,'password':password}).json()

        actual_code=data['code']
        # if actual_code != int(expected_code):
        #     log.error(f"登录请求失败,登陆账号: {username}, 密码: {password}, 期望code: {expected_code}, 实际code: {actual_code}, 响应信息: {resp.json()['message']}")            
        # assert actual_code == int(expected_code)
        assert_with_log(actual_code == int(expected_code),f"登录请求失败,登陆账号: {username}, 密码: {password}, 期望code: {expected_code}, 实际code: {actual_code}, 响应信息: {data['message']}")

    @allure.story("包含token登录")
    @allure.title("已登录状态下使用正确账号密码再次登录")
    def test_login_with_token(self):
        with allure.step("发送登录请求"):
            log.info("发送包含token的登录请求,账号: 'tester',密码: '123456'")
            data=self.api_client.post(path='login',json={'username':'tester','password':'123456'}).json()

        actual_code=data['code']
        assert_with_log(actual_code==0,f"重复登陆请求失败,预期状态码: 0,实际状态码: {actual_code},返回结果: {data}")
        assert_with_log(data['token']!=None,f"登录请求返回token出现异常,返回结果:{data}")
        