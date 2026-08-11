import pytest
import logging
import allure
import requests
from common.assert_util import assert_with_log
from common.init_apiclient import InitApiClient

log=logging.getLogger(__name__)

@pytest.mark.api
@pytest.mark.product
@allure.epic("小牛电商")
@allure.feature("商品模块-api")
class TestProduct(InitApiClient):

    @pytest.mark.smoke
    @allure.story("查询商品列表")
    @allure.title("包含有效token的情况下查询商品列表")
    def test_get_product_list(self):
        with allure.step("发送获取商品列表请求:"):
            log.info("获取商品列表")
            resp=self.api_client.get(path='products')

        actual_code=int(resp.json()['code'])
        # if actual_code != 0:
        #     log.error("获取商品列表失败,响应码: %d, 返回信息: %s", actual_code, resp.json()['message'])
        # assert actual_code == 0,"获取商品列表失败"

        assert_with_log(actual_code == 0,f"获取商品列表失败,响应码: {actual_code}, 返回信息: {resp.json()['message']}")

        products=resp.json()['products']

        assert_with_log(len(products)>0,"商品列表为空")
        # assert len(products) > 0,"商品列表为空"

        #进行商品字段验证
        required_fields=['id','name','price','stock']
        for product in products:
            for required_field in required_fields:
                assert_with_log(required_field in product,f"商品字段不完整,缺少字段:{required_field}")

            # if not product['price']>0:
            #     log.error(f"id为{product['id']}的商品价格异常")
            # assert product['price']>0 ,f"id为{product['id']}的商品价格异常"

            assert_with_log(product['price']>0,f"id为{product['id']}的商品价格异常")

            # if not product['stock']>=0:
            #     log.error(f"id为{product['id']}的商品库存数量异常")
            # assert product['stock']>=0 ,f"id为{product['id']}的商品库存数量异常"

            assert_with_log(product['stock']>=0,f"id为{product['id']}的商品库存数量异常")

        

    @allure.story("查询商品列表")
    @allure.title("无token的情况下查询商品列表")
    def test_get_product_list_without_token(self,base_url):
        with allure.step(f"没有token的情况下访问商品列表"):
            log.info("无token获取商品列表")
            resp=requests.request(method='get',
                                  url=f"{base_url}products")

        actual_code=int(resp.json()['code'])
        # if actual_code != 401:
        #     log.error(f"无token获取商品列表,不符合预期,预期响应码401,实际响应码{actual_code},响应内容{resp.json()}")
        # assert actual_code == 401

        assert_with_log(actual_code == 401,f"无token获取商品列表,不符合预期,预期响应码401,实际响应码{actual_code},响应内容{resp.json()}")

    @allure.story("查询商品列表")
    @allure.title("包含有效token的情况下查询商品列表")
    def test_add_0_quantity_product_to_cart(self):
        with allure.step(f"通过接口添加0库存商品进入购物车"):
            log.info("通过接口添加0库存商品进入购物车")
            resp=self.api_client.post(path='cart',
                                      json={'productId':104,
                                            'quantity':1})
        actual_code=int(resp.json()['code'])

        # if actual_code != 409:
        #     log.error(f"通过接口添加0库存商品出现,不符合预期,预期响应码409,实际响应码{actual_code},返回消息{resp.json()}")
        # assert actual_code == 409

        assert_with_log(actual_code == 409,f"通过接口添加0库存商品出现,不符合预期,预期响应码409,实际响应码{actual_code},返回消息{resp.json()}")
        