import pytest
import logging
import allure
import requests
import yaml
from common.assert_util import assert_with_log
from common.init_apiclient import InitApiClient

log=logging.getLogger(__name__)



@pytest.mark.api
@pytest.mark.pay
@allure.epic("小牛电商")
@allure.feature("支付模块-api")
class TestPay(InitApiClient):

    @allure.story("支付订单")
    @allure.title("支付未支付订单")
    def test_pay_unpaid_order(self,create_order):
        with allure.step("支付订单"):
            log.info(f"发送请求,支付未支付订单")
            data=self.api_client.post(path=f"orders/{create_order['order']['id']}/pay").json()

        actual_code=data['code']
        condition=actual_code==0
        message=f"支付未支付订单失败,预期响应码0,实际响应码:{actual_code},返回结果:{data}"
        assert_with_log(condition,message)

        order_status=data['order']['status']
        order_statusText=data['order']['statusText']
        condition=order_status=='paid' and order_statusText=='已支付'
        message=f"订单状态异常,预期状态status:'paid' ,statusText:'已支付',实际status:'{order_status}', statusText: {order_statusText}"
        assert_with_log(condition,message)

    @allure.story("支付订单")
    @allure.title("无token支付未支付订单")
    def test_pay_order_without_token(self,base_url,create_order):
        with allure.step("发送无token的请求,支付订单"):
            log.info("发送无token的请求,支付订单")
            data=requests.request(method='post',
                                  url=f"{base_url}orders/{create_order['order']['id']}/pay").json()

        actual_code=data['code']
        condition=actual_code==401
        message=f"无token支付未支付订单失败,预期响应码401,实际响应码:{actual_code},返回结果:{data}"
        assert_with_log(condition,message)

    @allure.story("支付订单")
    @allure.title("支付不存在的订单")
    def test_pay_unexist_order(self):
        with allure.step("支付订单"):
            log.info("发送支付请求")
            data=self.api_client.post(path='orders/12345/pay').json()

        actual_code=data['code']
        condition=actual_code==404
        message=f"支付不存在订单出现异常,预期响应码404,实际响应码:{actual_code},返回结果:{data}"
        assert_with_log(condition,message)

    @allure.story("支付订单")
    @allure.title("支付已支付的订单")
    @pytest.mark.xfail(reason="已知缺陷: 重复支付订单返回成功(code=0),预期400", strict=True)
    def test_pay_paid_order(self,create_order):
        with allure.step("两次支付订单"):
            log.info("发送两次支付订单请求")
            data=self.api_client.post(path=f"orders/{create_order['order']['id']}/pay").json()
            data=self.api_client.post(path=f"orders/{create_order['order']['id']}/pay").json()

        actual_code=data['code']
        condition=actual_code==400
        message=f"支付已支付订单出现异常,预期响应码400,实际响应码:{actual_code},返回结果:{data}"
        assert_with_log(condition,message)

    @allure.story("支付订单")
    @allure.title("支付已取消的订单")
    def test_pay_canceled_order(self,create_order):
        order_id=create_order['order']['id']
        with allure.step("取消订单"):
            log.info("发送取消订单请求")
            data=self.api_client.post(path=f'orders/{order_id}/cancel').json()
        with allure.step("支付已取消订单"):
            log.info("发送支付订单请求")
            data=self.api_client.post(path=f'orders/{order_id}/pay').json()

        actual_code=data['code']
        condition=actual_code==409
        message=f"支付已取消订单出现异常,预期响应码409,实际响应码:{actual_code},返回结果:{data}"
        assert_with_log(condition,message)

    @allure.story("支付订单")
    @allure.title("支付其他用户的订单")
    def test_pay_other_users_order(self,base_url,get_admin_token):
        with allure.step("添加商品进入购物车"):
            data=requests.request(method='post',
                                  url=f'{base_url}cart',
                                  json={'productId':101,'quantity':3},
                                  headers={'Authorization':f'Bearer {get_admin_token}'})
        with allure.step("创建订单"):
            data=requests.request(method='post',
                                  url=f'{base_url}orders',
                                  headers={'Authorization':f'Bearer {get_admin_token}'}).json()
        order_id=data['order']['id']
        with allure.step("支付订单"):
            data=self.api_client.post(path=f'orders/{order_id}/pay').json()

        actual_code=data['code']
        condition=actual_code==404
        message=f"支付其他用户订单出现异常,预期响应码404,实际响应码:{actual_code},返回结果:{data}"
        assert_with_log(condition,message)

    @allure.story("取消订单")
    @allure.title("取消待支付订单")
    @pytest.mark.xfail(reason="已知缺陷: 取消待支付订单后商品库存未回滚", strict=True)
    def test_cancel_unpaid_order(self,create_order):

        products=self.api_client.get(path='products').json()['products']
        order_items = create_order['order']['items']
        order_product_ids = {item['productId'] for item in order_items}

        stock_before_cancel={p['id']:p['stock'] for p in products if p['id'] in order_product_ids}

        with allure.step("取消订单"):
            log.info("发送取消订单请求")
            data=self.api_client.post(path=f"orders/{create_order['order']['id']}/cancel").json()

        actual_code=data['code']
        condition=actual_code==0
        message=f"取消待支付订单失败,预期响应码0,实际响应码:{actual_code},返回结果:{data}"
        assert_with_log(condition,message)

        products=self.api_client.get(path='products').json()['products']
        stock_after_cancel={p['id']:p['stock'] for p in products if p['id'] in order_product_ids}

        for item in order_items:
            product_id=item['productId']
            expect_stock=stock_before_cancel[product_id] + item['quantity']
            assert_with_log(expect_stock==stock_after_cancel[product_id],f"取消订单后库存未回滚, 商品id: {product_id}, 预期库存: {expect_stock}, 实际库存: {stock_after_cancel[product_id]}")


        order_status=data['order']['status']
        order_statusText=data['order']['statusText']
        condition=order_status=='cancelled' and order_statusText=='已取消'
        message=f"订单状态异常,预期状态status:'cancelled' ,statusText:'已取消',实际status:'{order_status}', statusText: {order_statusText}"
        assert_with_log(condition,message)

    @allure.story("取消订单")
    @allure.title("取消待支付订单")
    def test_cancel_order_without_token(self,base_url,create_order):
        with allure.step("取消订单"):
            log.info("发送取消订单请求")
            data=requests.request(method='post',
                                  url=f"{base_url}orders/{create_order['order']['id']}/cancel").json()

        actual_code=data['code']
        condition=actual_code==401
        message=f"无token取消订单失败,预期响应码401,实际响应码:{actual_code},返回结果:{data}"
        assert_with_log(condition,message)

    @allure.story("取消订单")
    @allure.title("取消已支付订单")
    def test_cancel_paid_order(self,create_order):
        order_id=create_order['order']['id']
        with allure.step("支付订单"):
            data=self.api_client.post(path=f'orders/{order_id}/pay').json()
        with allure.step("取消订单"):
            data=self.api_client.post(path=f'orders/{order_id}/cancel').json()

        actual_code=data['code']
        condition=actual_code==409
        message=f"取消已支付订单异常,预期响应码409,实际响应码:{actual_code},返回结果:{data}"
        assert_with_log(condition,message)

    @allure.story("取消订单")
    @allure.title("取消已取消订单")
    @pytest.mark.xfail(reason="已知缺陷: 重复取消订单返回成功(code=0),预期409", strict=True)
    def test_cancel_canceled_order(self,create_order):
        order_id=create_order['order']['id']
        with allure.step("两次取消订单"):
            data=self.api_client.post(path=f'orders/{order_id}/cancel').json()
            data=self.api_client.post(path=f'orders/{order_id}/cancel').json()

        actual_code=data['code']
        condition=actual_code==409
        message=f"取消已取消订单异常,预期响应码409,实际响应码:{actual_code},返回结果:{data}"
        assert_with_log(condition,message)

    @allure.story("取消订单")
    @allure.title("取消不存在订单")
    def test_cancel_unexist_order(self):
        with allure.step("取消订单"):
            data=self.api_client.post(path='orders/1234/cancel').json()

        actual_code=data['code']
        condition=actual_code==404
        message=f"取消不存在订单出现异常,预期响应码404,实际响应码:{actual_code},返回结果:{data}"
        assert_with_log(condition,message)

    @allure.story("取消订单")
    @allure.title("取消其他用户的订单")
    def test_cancel_other_users_order(self,base_url,get_admin_token):
        with allure.step("添加商品进入购物车"):
            data=requests.request(method='post',
                                  url=f'{base_url}cart',
                                  json={'productId':101,'quantity':3},
                                  headers={'Authorization':f'Bearer {get_admin_token}'})
        with allure.step("创建订单"):
            data=requests.request(method='post',
                                  url=f'{base_url}orders',
                                  headers={'Authorization':f'Bearer {get_admin_token}'}).json()
        order_id=data['order']['id']

        with allure.step("取消订单"):
            data=self.api_client.post(path=f'orders/{order_id}/cancel').json()

        actual_code=data['code']
        condition=actual_code==404
        message=f"取消其他用户订单异常,预期响应码404,实际响应码:{actual_code},返回结果:{data}"
        assert_with_log(condition,message)
