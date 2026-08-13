import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import allure
from common.assert_util import assert_with_log
import logging
from test_ui.pages.cart_page import CartPage
from test_ui.pages.product_page import ProductPage
from test_ui.pages.order_page import OrderPage
from common.yaml_util import load_yaml

@pytest.mark.ui
@pytest.mark.order_ui
class TestOrderUi:

    @pytest.fixture(autouse=True)
    def init(self,driver,login,api_client):
        self.product_page=ProductPage(driver)
        self.order_page=OrderPage(driver)
        self.cart_page=CartPage(driver)
        self.api_client=api_client

    @allure.story("创建订单")
    @allure.title("购物车不为空时,创建购物车")
    def test_create_order(self,add_products_to_cart):
        with allure.step("获取创建订单前商品库存"):
            for p in add_products_to_cart:
                p['pre_stock']=int(self.product_page.get_product_stock(p['productName']))

        with allure.step("点击'创建订单'按钮"):
            self.cart_page.click_create_order_button()

        toast=self.order_page.get_toast()
        self.order_page.wait_toast_invisible(toast)

        with allure.step("获取创建订单后商品库存"):
            for p in add_products_to_cart:
                p['after_stock']=int(self.product_page.get_product_stock(p['productName']))
                assert_with_log(p['pre_stock']-p['quantity']==p['after_stock'],f"商品库存扣减异常,预期: {p['pre_stock']-p['quantity']},实际: {p['after_stock']}")

        with allure.step("通过调用查询订单列表获取订单信息"):
            order_info=self.api_client.get(path='orders').json()['orders'][0]
            order_id=order_info['id']
            totalAmount=order_info['totalAmount']

        with allure.step("对比订单商品和购物车商品"):
            actual_items=self.order_page.get_order_items(order_id)
            expect_items={f"{p['productName']} × {p['quantity']}" for p in add_products_to_cart}

            assert_with_log(set(actual_items)==expect_items,f"订单商品与购物车不一致, 预期: {expect_items}, 实际: {set(actual_items)}")


        cart_empty_text=self.cart_page.get_cart_empty_text()
        assert_with_log(cart_empty_text=='购物车为空',f"创建订单后,购物车未清空")

        actual_totalAmount=self.order_page.get_order_amount(order_id)
        assert_with_log(actual_totalAmount==totalAmount,f"订单金额计算异常,预期: {actual_totalAmount},实际: {totalAmount}")

        actual_order_status=self.order_page.get_order_status(order_id)
        assert_with_log(actual_order_status=='待支付',f"订单状态异常,预期: 待支付,实际: {actual_order_status}")

    @allure.story("创建订单")
    @allure.title("购物车为空时,创建订单")
    def test_create_order_whem_empty_cart(self):
        with allure.step("点击'创建订单'按钮"):
            self.cart_page.click_create_order_button()

        toast=self.order_page.get_toast()
        assert_with_log(toast=='购物车为空，不能创建订单',f"购物车为空创建订单对应的toast文案异常,预期: '购物车为空，不能创建订单',实际: {toast}")

        empty_order_text=self.order_page.get_order_empty_text()
        assert_with_log(empty_order_text=='暂无订单',f'购物车为空时订单文案异常,实际: {empty_order_text}')

    @allure.story("创建订单")
    @allure.title("当购物车中存在商品数量大于库存时,创建订单")
    @pytest.mark.parametrize('testcase',load_yaml(r"test_ui\data\order.yaml"))
    def test_create_order_when_quantity_over_stock(self,testcase):
        with allure.step("添加商品进入购物车"):
            for product in testcase:
                response = self.api_client.post(
                    path='cart',
                    json={'productId': product['productId'], 'quantity': product['quantity']},
                )
                assert_with_log(response.status_code in (200, 201),
                                f'添加商品到购物车失败,实际状态码: {response.status_code}')
        with allure.step("点击'创建订单'按钮"):
            self.cart_page.click_create_order_button()

        with allure.step("断言toast提示库存不足"):
            toast = self.order_page.get_toast()   # 内部会等待toast可见

        assert_with_log('库存不足' in toast,
                        f"toast未提示库存不足, 实际: {toast}")

        over_stock_names=[p['productName'] for p in testcase if p['is_over_stock']]
        for name in over_stock_names:
            assert_with_log(name in toast,
                            f"toast未提示超库存商品'{name}', 实际: {toast}")
    @allure.story("查询订单")
    @allure.title("购物车为空时,查询购物车")
    def test_select_order_when_empty(self):
        with allure.step("定位元素"):
            empty_order_text=self.order_page.get_order_empty_text()

        assert_with_log(empty_order_text=='暂无订单',f"订单为空时,文案显示异常,预期文案: 暂无订单,实际文案: {empty_order_text}")


    @allure.story("检查订单ui")
    @allure.title("检查刷新订单按钮")
    def test_refresh_button(self,add_products_to_cart):
        with allure.step("定位'刷新订单'按钮"):
            refresh_button_text=self.order_page.get_refresh_button_text()
            refresh_button_is_enable=self.order_page.refresh_button_is_enable()

        assert_with_log(refresh_button_text=='刷新订单',f"'刷新订单'按钮文案异常,预期文案:刷新订单,实际文案:{refresh_button_text}")
        assert_with_log(refresh_button_is_enable,f"'刷新订单'按钮不可用")

        with allure.step("通过UI创建订单"):
            self.cart_page.click_create_order_button()
            self.order_page.wait_for_order_count(1)
            order_id=self.api_client.get(path='orders').json()['orders'][0]['id']

        with allure.step("通过接口支付,不会自动刷新页面"):
            self.api_client.post(path=f"orders/{order_id}/pay")

        with allure.step("获取刷新前的订单状态"):
            pre_order_status=self.order_page.get_order_status(order_id)
            assert_with_log(pre_order_status=='待支付', "支付成功后,刷新前页面应仍显示待支付")

        with allure.step("点击'刷新订单'按钮"):
            self.order_page.click_refresh_button()

        with allure.step("获取刷新后的订单状态"):
            # 刷新是异步的,等待状态变为期望值再断言
            self.order_page.wait_for_order_status(order_id, '已支付')
            after_order_status=self.order_page.get_order_status(order_id)

        assert_with_log(after_order_status=='已支付',"刷新后订单状态应为已支付")
