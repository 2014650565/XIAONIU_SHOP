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
@pytest.mark.pay_ui
@allure.epic("小牛电商")
@allure.feature("支付模块-ui")
class TestPayUi:

    @pytest.fixture(autouse=True)
    def init_page(self,driver,login):
        self.order_page=OrderPage(driver)

    @pytest.fixture(scope='function')
    def order_id(self,create_order):
        yield create_order['order']['id']

    @allure.story("支付订单")
    @allure.title("支付未支付订单")
    def test_pay_unpaid_order(self,order_id):
        self.order_page.click_refresh_button()
        self.order_page.wait_for_order_count(1)
        pay_button_text=self.order_page.get_pay_button(order_id).text
        pay_button_is_enable=self.order_page.pay_button_is_enable(order_id)
        assert_with_log(pay_button_text=='支付',f"'支付'按钮文案异常,预期文案:支付,实际文案:{pay_button_text}")
        assert_with_log(pay_button_is_enable,f"'支付'按钮不可用")

        with allure.step("点击'支付'按钮"):
            self.order_page.click_pay_button(order_id)

        toast=self.order_page.get_toast()
        assert_with_log(toast=='支付成功',f"支付待支付订单对应的toast文案异常,预期: '支付成功',实际: {toast}")
        self.order_page.wait_for_order_status(order_id, '已支付')

        order_status=self.order_page.get_order_status(order_id)
        assert_with_log(order_status=='已支付',f"订单状态异常,已支付订单状态应为: '已支付',实际状态: {order_status}")

    @allure.story("支付订单")
    @allure.title("支付已支付订单")
    @pytest.mark.xfail(reason="已知缺陷: 重复支付订单toast为'支付成功',预期'支付失败,订单已支付'", strict=True)
    def test_pay_paid_order(self,order_id):
        self.order_page.click_refresh_button()
        self.order_page.wait_for_order_count(1)
        with allure.step("点击'支付'按钮"):
            self.order_page.click_pay_button(order_id)
        toast=self.order_page.get_toast()
        self.order_page.wait_toast_invisible('支付成功')
        with allure.step("再次点击'支付'按钮"):
            self.order_page.click_pay_button(order_id)

        toast=self.order_page.get_toast()
        assert_with_log(toast=='支付失败,订单已支付',f"重复支付订单toast异常,预期:'支付失败,订单已支付',实际: {toast}")
        self.order_page.wait_for_order_status(order_id, '已支付')
        order_status=self.order_page.get_order_status(order_id)
        assert_with_log(order_status=='已支付',f"支付已支付订单状态异常,预期:'已支付',实际: {order_status}")


    @allure.story("支付订单")
    @allure.title("支付已取消订单")
    def test_pay_canceled_order(self,order_id):
        self.order_page.click_refresh_button()
        self.order_page.wait_for_order_count(1)
        with allure.step("点击'取消'按钮"):
            self.order_page.click_cancel_button(order_id)

        toast=self.order_page.get_toast()
        self.order_page.wait_toast_invisible('订单已取消')

        with allure.step("点击'支付'按钮"):
            self.order_page.click_pay_button(order_id)

        toast=self.order_page.get_toast()
        assert_with_log(toast=='已取消订单不能支付',f"支付已取消订单toast异常,预期:'已取消订单不能支付',实际: {toast}")
        self.order_page.wait_for_order_status(order_id, '已取消')

        order_status=self.order_page.get_order_status(order_id)
        assert_with_log(order_status=='已取消',f"订单状态异常,预期:'已取消',实际: {order_status}")

    @allure.story("取消订单")
    @allure.title("取消待支付订单")
    def test_cancel_unpaid_order(self,order_id):
        self.order_page.click_refresh_button()
        self.order_page.wait_for_order_count(1)
        with allure.step("点击'取消'按钮"):
            self.order_page.click_cancel_button(order_id)

        toast=self.order_page.get_toast()
        assert_with_log(toast=='订单已取消',f"取消待支付订单toast异常,预期:'订单已取消',实际: {toast}")
        self.order_page.wait_for_order_status(order_id, '已取消')
        order_status=self.order_page.get_order_status(order_id)
        assert_with_log(order_status=='已取消',f"取消待支付订单状态异常,预期:'已取消',实际: {order_status}")

    @allure.story("取消订单")
    @allure.title("取消已支付订单")
    def test_cancel_paid_order(self,order_id):
        self.order_page.click_refresh_button()
        self.order_page.wait_for_order_count(1)
        with allure.step("点击'支付'按钮"):
            self.order_page.click_pay_button(order_id)
        toast=self.order_page.get_toast()
        self.order_page.wait_toast_invisible('支付成功')

        with allure.step("点击'取消'按钮"):
            self.order_page.click_cancel_button(order_id)

        toast=self.order_page.get_toast()
        assert_with_log(toast=='已支付订单不能取消，请走退款流程',f"取消已支付订单toast异常,预期:'已支付订单不能取消，请走退款流程',实际: {toast}")
        self.order_page.wait_for_order_status(order_id, '已支付')
        order_status=self.order_page.get_order_status(order_id)
        assert_with_log(order_status=='已支付',f"取消已支付订单状态异常,预期:'已支付',实际: {order_status}")

    @allure.story("取消订单")
    @allure.title("取消已取消订单")
    @pytest.mark.xfail(reason="已知缺陷: 重复取消订单toast为'订单已取消',预期'取消失败,已取消订单不能重复取消'", strict=True)
    def test_cancel_canceled_order(self,order_id):
        self.order_page.click_refresh_button()
        self.order_page.wait_for_order_count(1)
        with allure.step("点击'取消'按钮"):
            self.order_page.click_cancel_button(order_id)
        toast=self.order_page.get_toast()
        self.order_page.wait_toast_invisible('订单已取消')

        with allure.step("点击'取消'按钮"):
            self.order_page.click_cancel_button(order_id)
        toast=self.order_page.get_toast()
        assert_with_log(toast=='取消失败，已取消订单不能重复取消',f"取消已取消订单toast异常,预期:'取消失败，已取消订单不能重复取消',实际: {toast}")
        self.order_page.wait_for_order_status(order_id, '已取消')
        order_status=self.order_page.get_order_status(order_id)
        assert_with_log(order_status=='已取消',f"取消已取消订单状态异常,预期:'已取消',实际: {order_status}")



    
