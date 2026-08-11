import pytest
import logging
import allure
import requests
import yaml
from common.assert_util import assert_with_log
from datetime import datetime
from common.init_apiclient import InitApiClient

log=logging.getLogger(__name__)

@pytest.mark.api
@pytest.mark.order
@allure.epic("小牛电商")
@allure.feature("订单模块-api")
class TestOrder(InitApiClient):

    @allure.story("创建订单")
    @allure.title("购物车不为空时,创建订单")
    @pytest.mark.smoke
    def test_create_order(self,add_products_to_cart):
        # with allure.step("确保购物车不为空"):
        #     log.info("获取购物车信息")
        #     resp=self.api_client.get(path='cart')
        #     if len(resp.json()['items'])==0:
        #         product_id,quantity=103,1
        #         log.info(f"购物车为空,需要向购物车中添加id为: {product_id},且库存大于{quantity-1}的商品")
        #         self.api_client.post(path='cart',
        #                              json={'productId':product_id,
        #                                    'quantity':quantity})

        with allure.step("获取创建订单前,商品数量"):
            log.info("发送查询商品列表请求")
            data=self.api_client.get(path='products').json()

        this_products=add_products_to_cart
        for p in data['products']:
            for tp in this_products:
                if p['id']==tp['productId']:
                    tp['pre_quantity']=p['stock']
                    tp['expect_quantity']=tp['pre_quantity']-tp['quantity']


        with allure.step("通过接口创建订单"):
            log.info("发送创建订单的请求")
            data=self.api_client.post(path='orders').json()

        #断言响应码
        actual_code=int(data['code'])
        message=f"创建订单失败,预期响应码0,实际响应码{actual_code},返回信息{data}"
        condition=actual_code == 0
        assert_with_log(condition,message)
        # if not actual_code == 0:
        #     log.error(message)
        # assert actual_code == 0,message

        #断言字段完整性
        keys=data['order'].keys()
        required_keys=['id','userId','items','totalAmount', 'status', 'createdAt', 'statusText']
        condition=set(keys)==set(required_keys)
        message=f"字段完整性验证异常,缺少字段: {set(required_keys)-set(keys)}"
        assert_with_log(condition,message)

        #断言金额
        sum_price=sum(p['subtotal'] for p in data['order']['items'])
        condition=sum_price == data['order']['totalAmount']
        message=f"订单金额异常,预计金额: {sum_price},实际金额: {data['order']['totalAmount']}"
        assert_with_log(condition,message)
        # if not condition:
        #     log.error(message)
        # assert condition,message

        #断言订单状态
        condition=data['order']['status']=='pending' and data['order']['statusText']=='待支付'
        message=f"订单状态异常,预期status: pending, 预期statusText: 待支付, 实际status: {data['order']['status']},实际statusText: {data['order']['statusText']}"
        assert_with_log(condition,message)
        # if not condition:
        #     log.error(message)
        # assert condition,message

        #断言购物车清空
        with allure.step("查询购物车列表"):
            data=self.api_client.get(path='cart').json()
        condition=len(data['items'])==0
        message=f"购物车未清空,返回购物车信息: {data['items']}"
        assert_with_log(condition,message)

        with allure.step('获取创建订单后,商品库存'):
            log.info('发送查询商品列表订单')
            data=self.api_client.get(path='products').json()
        for p in data['products']:
            for tp in this_products:
                if p['id']==tp['productId']:
                    tp['now_quantity']=p['stock']

        for p in this_products:
            condition=p['now_quantity']==p['expect_quantity']
            message=f"库存更新异常,商品id: {p['productId']},商品名称: {p['productName']},预期库存: {p['expect_quantity']},实际库存: {p['now_quantity']}"
            assert_with_log(condition,message)

        # condition=all(p['now_quantity']==p['expect_quantity'] for p in this_products)
        # message=f"库存更新异常,预期库存为: {p}"
        # assert_with_log(condition,message)

    @allure.story("创建订单")
    @allure.title("购物车为空时,创建订单")
    def test_create_order_when_cart_is_empty(self):
        with allure.step("发送创建订单请求"):
            log.info("当购物车为空时创建订单")
            data=self.api_client.post(path='orders').json()

        actual_code=int(data['code'])
        condition=actual_code == 400
        message=f"创建订单失败,预期响应码400,实际响应码{actual_code},返回信息{data}"

        assert_with_log(condition,message)
        # if not condition:
        #     log.error(message)
        # assert condition,message

    @allure.story("创建订单")
    @allure.title("token为空时,创建订单")
    def test_create_order_without_token(self,base_url):
        with allure.step("发送创建订单请求"):
            log.info("没有token发送创建订单请求")
            data=requests.request(method='post',
                                  url=f'{base_url}orders').json()

        actual_code=data['code']
        condition=actual_code==401
        message=f"无token创建订单出现异常,预期状态码: 401,实际状态码: {actual_code},返回信息: {data}"

        assert_with_log(condition,message)

    @allure.story("创建订单")
    @allure.title("购物车中存在一个商品数量大于库存时,创建订单")
    def test_create_order_when_one_product_quantity_over_stock(self):
        product_name,product_id,quantity='接口自动化课程',101,999
        with allure.step("向购物车中添加一个商品,要求数量超过库存"):
            log.info("向购物车中添加一个商品,要求数量超过库存")
            data=self.api_client.post(path='cart',
                                      json={'productId':product_id,
                                            'quantity':quantity}).json()

        with allure.step("发送创建订单请求"):
            log.info("发送创建订单请求")
            data=self.api_client.post(path='orders').json()

        actual_code=data['code']
        condition=actual_code==409
        message=f"购物车中存在商品数量超出库存时创建订单,结果与预期不符,预期状态码: 409,实际状态码: {actual_code},返回信息: {data}"
        assert_with_log(condition,message)

        condition=product_name in data['message']
        message=f"message应包含超库存商品名'接口自动化课程', 实际: {data['message']}"
        assert_with_log(condition,message)

    @allure.story("创建订单")
    @allure.title("购物车中存在多个商品数量大于库存时,创建订单")
    def test_create_order_when_more_than_one_product_quantity_over_stock(self):
        products=[{'productId':101,'quantity':999,'productName':'接口自动化课程'},{'productId':102,'quantity':999,'productName':'性能测试训练营'}]
        with allure.step("向购物车中添加多个数量超出库存的商品"):
            for p in products:
                log.info(f"向购物车中添加id为: {p['productId']},数量为: {p['quantity']}超出库存的商品")
                data=self.api_client.post(path='cart',
                                        json=p).json()

        with allure.step("发送创建订单请求"):
            log.info("发送创建订单请求")
            data=self.api_client.post(path='orders').json()

        actual_code=data['code']
        product_name_list=[p['productName'] for p in products]
        condition=all(name in data['message'] for name in product_name_list)
        message = f"message应包含所有超库存商品名: {product_name_list}, 实际: {data['message']}"
        assert_with_log(condition, message)

    @allure.story("查询订单")
    @allure.title("订单为空时,查询订单")
    def test_select_orders_when_empty(self):
        with allure.step("发送查询订单请求"):
            log.info("订单为空时,发送查询订单请求")
            data=self.api_client.get(path='orders').json()

        actual_code=data['code']
        orders_length=len(data['orders'])
        condition=actual_code==0
        message=f"订单为空时,查询订单失败,预期响应码0,实际响应码{actual_code},返回信息{data}"
        assert_with_log(condition,message)

        condition=orders_length==0
        message=f"订单为空时,查询订单异常,预期订单数量: 0,实际订单数量{orders_length},返回实际订单{data['orders']}"
        assert_with_log(condition,message)

    @allure.story("查询订单")
    @allure.title("订单不为空时,查询订单")
    def test_select_orders(self,get_products):
        # products=[{'productId':103,'quantity':1}]
        # with allure.step("添加商品到购物车"):
        #     for p in products:
        #         log.info(f"添加id为: {p['productId']},数量为: {p['quantity']}的商品到购物车")
        #         self.api_client.post(path='cart',
        #                             json={'productId':p['productId'],
        #                                 'quantity':p['quantity']})
        # with allure.step("创建订单"):
        #     log.info("创建订单")
        #     self.api_client.post(path='orders')

        expect_orders_lengt=len(get_products)
        with allure.step("创建多个订单"):
            for p in get_products:
                self.api_client.post(path='cart',json={'productId':p['productId'],'quantity':p['quantity']})
                self.api_client.post(path='orders')

        with allure.step("查询订单"):
            log.info("查询订单")
            data=self.api_client.get(path='orders').json()

        actual_code=data['code']
        orders_length=len(data['orders'])
        #断言响应码
        condition=actual_code==0
        message=f"查询订单失败,预期响应码0,实际响应码{actual_code},返回信息{data}"
        assert_with_log(condition,message)

        #断言user_id
        id_set={order['userId'] for order in data['orders']}
        assert_with_log(len(id_set)==1,f"查询订单出现异常,出现其他用户订单,返回订单: {data['orders']}")
        assert_with_log(1 in id_set,f"查询订单出现异常,查询的订单为其他用户的")


        #断言订单数量
        condition=orders_length==expect_orders_lengt
        message=f"查询订单异常,预期订单数量: {expect_orders_lengt},实际订单数量{orders_length},返回实际订单{data['orders']}"
        assert_with_log(condition,message)

        #断言按时间倒序排列
        actual_time=[order['createdAt'] for order in data['orders']]
        sorted_time=sorted([datetime.strptime(t,'%Y/%m/%d %H:%M:%S') for t in actual_time],
                           reverse=True)

        condition=[datetime.strptime(t,'%Y/%m/%d %H:%M:%S') for t in actual_time]==sorted_time
        message=f"订单未按时间倒序排列, 实际顺序: {actual_time}"
        assert_with_log(condition,message)


    @allure.story("查询订单")
    @allure.title("token为空时,查询订单")
    def test_select_orders_without_token(self,base_url):
        with allure.step("发送查询订单请求"):
            log.info("没有token发送查询订单请求")
            data=requests.request(method='get',
                                  url=f'{base_url}orders').json()

        actual_code=data['code']
        condition=actual_code==401
        message=f"token为空时,查询订单失败,预期响应码401,实际响应码{actual_code},返回信息{data}"
        assert_with_log(condition,message)

    @allure.story("根据id查询订单详情")
    @allure.title("订单id存在时,查询订单详情")
    def test_select_order_by_id(self,add_products_to_cart):
        with allure.step("创建订单"):
            log.info("发送创建订单请求")
            data=self.api_client.post(path='orders').json()

        order_id=data['order']['id']
        with allure.step("通过id查询订单详情"):
            log.info("通过id查询订单详情")
            data=self.api_client.get(path=f'orders/{order_id}').json()

        actual_code=data['code']
        condition=actual_code==0
        message=f"通过id查询订单详情失败,预期响应码0,实际响应码{actual_code},返回信息{data}"
        assert_with_log(condition,message)

        
        condition=data['order']['userId']==1
        message=f"查询订单出现异常,查询的订单为其他用户的"
        assert_with_log(condition,message)

        required_keys=['id','userId','items','totalAmount','status','createdAt','statusText']
        actual_keys=data['order'].keys()
        condition=all(rk in actual_keys for rk in required_keys)
        message=f"字段完整性验证异常,预期完整字段: {required_keys},实际字段: {actual_keys}"
        assert_with_log(condition,message)

        sum_price=sum(p['subtotal'] for p in data['order']['items'])
        condition=sum_price==data['order']['totalAmount']
        message=f"订单金额出现异常,预期金额: {sum_price},实际金额: {data['order']['totalAmount']}"
        assert_with_log(condition,message)

    @allure.story("根据id查询订单详情")
    @allure.title("token不存在时,查询订单详情")
    def test_select_order_by_id_without_token(self,base_url,add_products_to_cart):
        with allure.step("创建订单,获取id"):
            log.info("发送创建订单请求")
            data=self.api_client.post(path='orders').json()
        order_id=data['order']['id']
        
        with allure.step("发送根据id查询订单的请求"):
            log.info(f"发送根据id: {order_id}查询订单的请求")
            data=requests.request(method='get',
                                  url=f'{base_url}orders/{order_id}').json()

        actual_code=data['code']
        condition=actual_code==401
        message=f"根据订单id: {order_id},查询订单详情出现异常,预期响应码401,实际响应码{actual_code},返回信息{data}"
        assert_with_log(condition,message)


    @allure.story("根据id查询订单详情")
    @allure.title("订单id不存在时,查询订单详情")
    def test_select_order_by_unexist_id(self):
        unexist_order_id='12345'
        
        with allure.step("发送根据id查询订单请求"):
            log.info(f"发送根据id: {unexist_order_id}查询订单请求")
            data=self.api_client.get(path=f'orders/{unexist_order_id}').json()

        actual_code=data['code']
        condition=actual_code==404
        message=f"根据不存在的订单id: {unexist_order_id},查询订单详情出现异常,预期响应码404,实际响应码{actual_code},返回信息{data}"
        assert_with_log(condition,message)

    @allure.story("根据id查询订单详情")
    @allure.title("订单id不存在时,查询订单详情")
    def test_select_order_by_others_id(self,base_url,get_admin_token):
        with allure.step('用其他账户添加商品到购物车'):
            log.info('用其他账户添加商品到购物车')
            data=requests.request(method='post',
                                  url=f'{base_url}cart',
                                  json={'productId':101,'quantity':1},
                                  headers={'Authorization':f'Bearer {get_admin_token}'}).json()
        with allure.step('创建订单'):
            log.info('发送创建订单请求')
            data=requests.request(method='post',
                                  url=f'{base_url}orders',
                                  headers={'Authorization':f'Bearer {get_admin_token}'}).json()
        other_user_order_id=data['order']['id']

        with allure.step('根据id查询订单详情'):
            log.info(f"根据其他用户的订单id: {other_user_order_id},查询订单详情")
            data=self.api_client.get(path=f'orders/{other_user_order_id}').json()

        actual_code=data['code']
        condition=actual_code==404
        message=f"根据其他用户的订单id: {other_user_order_id},查询订单详情出现异常,预期响应码404,实际响应码{actual_code},返回信息{data}"
        assert_with_log(condition,message)


