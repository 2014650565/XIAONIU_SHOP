import pytest
import logging
import allure
import requests
from common.assert_util import assert_with_log
from common.yaml_util import load_yaml
from common.init_apiclient import InitApiClient

log=logging.getLogger(__name__)




@pytest.mark.api
@pytest.mark.cart
@allure.epic("小牛电商")
@allure.feature("购物车模块-api")
class TestCart(InitApiClient):


    @pytest.mark.smoke
    @allure.story("查询购物车")
    @allure.title("购物车不为空时,查询购物车")
    def test_select_cart(self,add_products_to_cart):
        # product_id,quantity=103,3
        # with allure.step(f"提前向购物车中添加id为: {product_id},数量: {quantity}的商品"):
        #     log.info(f"向购物车中添加id为: {product_id},数量: {quantity}的商品")
        #     self.api_client.post(path='cart',
        #                          json={'productId':product_id,
        #                                'quantity':quantity})
        with allure.step("获取购物车商品列表"):
            log.info("获取购物车商品列表")
            resp=self.api_client.get(path='cart')

        actual_code=int(resp.json()['code'])
        message=f"获取购物车商品列表失败,预期响应码0,实际响应码{actual_code},返回信息{resp.json()}"
        # if not actual_code == 0:
        #     log.error(message)
        # assert actual_code==0,message

        assert_with_log(actual_code==0,message)

        sum_price=sum(p['subtotal'] for p in resp.json()['items'])
        # for product in resp.json()['items']:
        #     sum_price = sum_price+product['subtotal']
        
        condition=sum_price==resp.json()['totalAmount']
        message=f"购物车总金额异常,实际总金额:{sum_price},购物车总金额:{resp.json()['totalAmount']}"
        # if not condition:
        #     log.error(message)
        # assert condition,message
        assert_with_log(condition,message)

    @allure.story("查询购物车")
    @allure.title("购物车为空时,查询购物车")
    def test_select_cart_when_empty(self):
        with allure.step("发送查询购物车商品列表请求"):
            log.info("发送查询购物车商品列表请求")
            resp=self.api_client.get(path='cart')

        actual_code=int(resp.json()['code'])
        message=f"获取购物车商品列表失败,预期响应码0,实际响应码{actual_code},返回信息{resp.json()}"
        # if not actual_code == 0:
        #     log.error(message)
        # assert actual_code==0,message   
        assert_with_log(actual_code == 0,message)

        length=len(resp.json()['items'])
        message=f"购物车商品为空时,查询购物车列表出现异常,购物车中存在{length}个商品:{resp.json()['items']}"
        # if not length == 0:
        #     log.error(message)
        # assert length == 0,message
        assert_with_log(length == 0,message)

    @allure.story("查询购物车")
    @allure.title("token为空时,查询购物车")
    def test_select_cart_without_token(self,base_url):
        with allure.step("在没有token的情况下查询购物车信息"):
            log.info("在没有token的情况下查询购物车信息")
            resp=requests.request(method='get',
                                  url=f"{base_url}cart")

        actual_code=int(resp.json()['code'])
        message=f"无token获取购物车信息,与预期不符,预期状态码:401,实际响应码:{actual_code},响应内容:{resp.json()}"
        # if not actual_code == 401:
        #     log.error(message)
        # assert actual_code == 401,message
        assert_with_log(actual_code == 401,message)


    @allure.story("添加商品到购物车")
    @allure.title("添加商品id: {testcase[product_id]},数量: {testcase[quantity]}")
    @pytest.mark.parametrize('testcase',load_yaml(r"test_api/data/cart_data.yaml"))
    def test_add_product_to_cart(self,testcase):
        if testcase['quantity'] is None:
            pytest.xfail("已知缺陷: 数量为空时系统返回成功(code=0),预期400")
        if testcase['quantity'] == 0:
            pytest.xfail("已知缺陷: 添加数量0的商品时系统返回成功(code=0),预期400")
        with allure.step("添加商品到购物车"):
            log.info(f"添加商品进入购物车,商品id:{testcase['product_id']},数量:{testcase['quantity']}")
            resp=self.api_client.post(path='cart',
                                      json={'productId':testcase['product_id'],
                                            'quantity':testcase['quantity']})
        actual_code=resp.json()['code']
        message=f"添加商品到购物车,与预期不符,预期响应码:{testcase['expected_code']},实际响应码:{actual_code},响应内容:{resp.json()}"
        # if not actual_code == testcase['expected_code']:
        #     log.error(message)
        # assert actual_code == testcase['expected_code'],message
        assert_with_log(actual_code == testcase['expected_code'],message)
        

    @allure.story("添加商品到购物车")
    @allure.title("没有token的情况下添加商品到购物车")
    def test_add_product_to_cart_without_token(self,base_url):
        with allure.step("发送没有token的请求,添加商品到购物车"):
            log.info(f"无token添加商品到购物车,商品id: 101, 数量: 1")
            resp=requests.request(method='post',
                                  url=f'{base_url}cart',
                                  json={'productId':101,
                                        'quantity':1})

        actual_code=int(resp.json()['code'])
        message=f"无token添加商品到购物车,与预期不符,预期状态码:401,实际响应码:{actual_code},响应内容:{resp.json()}"
        # if not actual_code == 401:
        #     log.error(message)
        # assert actual_code == 401,message
        assert_with_log(actual_code == 401,message)


    @allure.story("删除购物车商品")
    @allure.title("购物车不为空时,删除购物车商品")
    def test_delete_cart(self):
        product_id=103
        with allure.step("向购物车中提前添加库存不为0的商品,以满足删除条件"):
            log.info(f"向购物车中添加id为{product_id}的商品")
            resp=self.api_client.post(path='cart',
                                 json={'productId':product_id,
                                       'quantity':2})
            
        with allure.step("查询购物车金额和数量"):
            log.info("发送查询购物车信息的请求,以确认购物车金额和数量")
            resp=self.api_client.get(path='cart')

        past_amount=resp.json()['totalAmount']
        past_len=len(resp.json()['items'])
        subtotal=next((p['subtotal'] for p in resp.json()['items'] if p['productId']==product_id), 0)
        
        with allure.step("删除购物车商品"):
            log.info(f"删除id为{product_id}的购物车商品")
            resp=self.api_client.delete(path=f'cart/{product_id}')

        with allure.step("再次查询购物车商品,查询购物车金额和数量是否更新"):
            log.info("再次发送查询购物车信息的请求,以确认购物车信息更新")
            resp=self.api_client.get(path='cart')

        now_amount=resp.json()['totalAmount']
        now_len=len(resp.json()['items'])
        

        actual_code=int(resp.json()['code'])
        message=f"删除购物车商品异常,预期状态码:0,实际响应码:{actual_code},响应内容:{resp.json()}"
        # if not actual_code == 0:
        #     log.error(message)
        # assert actual_code == 0,message
        assert_with_log(actual_code == 0,message)

        message=f"删除购物车商品时,商品数量出现异常,预期数量: {past_len-1},实际数量: {now_len}"
        # if not past_len-now_len==1:
        #     log.error(message)
        # assert past_len-now_len==1,message
        assert_with_log(past_len-now_len==1,message)

        message=f"删除购物车商品时,商品金额出现异常,预期金额: {past_amount-subtotal},实际金额: {now_amount}"
        # if not past_amount-subtotal==now_amount:
        #     log.error(message)
        # assert past_amount-subtotal==now_amount,message
        assert_with_log(past_amount-subtotal==now_amount,message)


    @allure.story("删除购物车商品")
    @allure.title("token为空时,删除购物车商品")
    def test_delete_cart_without_token(self,base_url):
        product_id=103
        with allure.step("发送没有token的请求,删除购物车商品"):
            log.info(f"没有token删除id为{product_id}的购物车商品")
            resp=requests.request(method='delete',
                                  url=f'{base_url}cart/{product_id}')

        actual_code=int(resp.json()['code'])
        message=f"无token删除购物车商品,与预期不符,预期状态码:401,实际响应码:{actual_code},响应内容:{resp.json()}"
        # if not actual_code == 401:
        #     log.error(message)
        # assert actual_code == 401,message
        assert_with_log(actual_code == 401,message)

    @allure.story("删除购物车商品")
    @allure.title("删除购物车中不存在的商品")
    @pytest.mark.xfail(reason="已知缺陷: 删除购物车中不存在的商品时系统返回成功(code=0),预期404", strict=True)
    def test_delete_not_exit_product_in_cart(self):
        product_id=103
        with allure.step(f"查询购物车中是否有id为: {product_id} 的商品"):
            log.info(f"查询购物车信息")
            resp=self.api_client.get(path='cart')

        product=next((p for p in resp.json()['items'] if p['productId']==product_id),0)
        if product != 0:
            with allure.step(f"购物车中存在id为{product_id}的商品,提前删除"):
                log.info(f"删除id为: {product_id} 的商品")
                resp=self.api_client.delete(path=f'cart/{product_id}')

        with allure.step("发送删除商品请求"):
            log.info(f"删除id为: {product_id} 的商品")
            resp=self.api_client.delete(path=f'cart/{product_id}')

        actual_code=int(resp.json()['code'])
        message=f"删除购物车中不存在的商品,与预期不符,预期状态码:404,实际响应码:{actual_code},响应内容:{resp.json()}"
        # if not actual_code == 404:
        #     log.error(message)
        # assert actual_code == 404,message
        assert_with_log(actual_code == 404,message)
        


    @allure.story("删除购物车商品")
    @allure.title("删除系统中不存在的商品")
    @pytest.mark.xfail(reason="已知缺陷: 删除系统中不存在的商品时系统返回成功(code=0),预期404", strict=True)
    def test_delete_no_exit_product(self):
        product_id=9999
        with allure.step(f"删除系统中不存在的商品"):
            log.info(f"删除系统中不存在的商品,id为: {product_id}")
            resp=self.api_client.delete(path=f'cart/{product_id}')

        actual_code=int(resp.json()['code'])
        message=f"删除系统中不存在的商品,与预期不符,预期状态码:404,实际响应码:{actual_code},响应内容:{resp.json()}"
        # if not actual_code == 404:
        #     log.error(message)
        # assert actual_code == 404,message
        assert_with_log(actual_code == 404,message)
