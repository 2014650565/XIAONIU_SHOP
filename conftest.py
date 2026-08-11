import pytest
import requests
from common.api_client import ApiClient
import logging
import allure

log=logging.getLogger(__name__)

@pytest.fixture(scope='session',autouse=True)
def testFixture():
    print("用例开始")
    yield
    print("\n用例结束")


@pytest.fixture(scope='session')
def base_url():
    yield "http://43.133.227.52/api/"

@pytest.fixture(scope='session')
def get_token(base_url):
    resp=requests.request(url=f"{base_url}login",
                          method='post',
                          json={"username":"tester",
                                "password":"123456"})
    yield resp.json()['token']

@pytest.fixture(scope='session')
def get_admin_token(base_url):
    resp=requests.request(url=f"{base_url}login",
                          method='post',
                          json={"username":"admin",
                                "password":"admin123"})
    yield resp.json()['token']

@pytest.fixture(scope='session')
def api_client(base_url,get_token):
    yield ApiClient(base_url,get_token)


@pytest.fixture(scope='function',autouse=True)
def reset_test_data(base_url,get_admin_token):
    requests.request(method='post',
                     url=f'{base_url}reset',
                     headers={"Authorization":f'Bearer {get_admin_token}'})

@pytest.fixture(scope='function')
def get_products():
    yield [{'productId':101,'quantity':1,'productName':'接口自动化课程'},{'productId':103,'quantity':2,'productName':'AI测试资料包'}]

@pytest.fixture(scope='function')
def add_products_to_cart(base_url,get_token,get_products):
    # products=[{'productId':101,'quantity':1,'productName':'接口自动化课程'},{'productId':103,'quantity':2,'productName':'AI测试资料包'}]
    with allure.step("添加商品到购物车"):
        for p in get_products:
            log.info(f"添加id为: {p['productId']},数量为: {p['quantity']}的商品进入购物车")
            requests.request(method='post',
                            url=f'{base_url}cart',
                            json={'productId':p['productId'],
                                'quantity':p['quantity']},
                            headers={"Authorization":f"Bearer {get_token}"})

    yield get_products

@pytest.fixture(scope='function')
def create_order(base_url,get_token,add_products_to_cart):
    with allure.step("创建订单"):
        log.info("发送创建订单请求")
        data=requests.request(method='post',
                         url=f'{base_url}orders',
                         headers={'Authorization': f'Bearer {get_token}'}).json()
    yield data




if __name__=="__main__":
    pass