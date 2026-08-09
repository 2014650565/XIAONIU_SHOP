import requests
import pytest
import allure
import logging
from common.assert_util import assert_with_log

log= logging.getLogger(__name__)

@pytest.mark.api
@pytest.mark.health
@allure.epic('小牛电商')
@allure.feature('健康模块')
class TestHealth:

    @allure.story('健康测试')
    def test_health(self, base_url):
        with allure.step("健康测试"):
            log.info("发送健康检查请求")
            resp=requests.request(method='get',
                                url=f"{base_url}health")

        actual_code=int(resp.json()['code'])
        message=f"健康检查异常,预期响应码0,实际响应码{actual_code},返回消息{resp.json()['message']}"
        assert_with_log(actual_code == 0,message)

        # actual_code=int(resp.json()['code'])
        # if not actual_code == 0:
        #     log.critical(f"健康检查异常,预期响应码0,实际响应码{actual_code},返回消息{resp.json()['message']}")

        # assert actual_code == 0