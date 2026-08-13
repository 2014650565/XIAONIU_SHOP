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
from common.csv_util import csv_load


@pytest.mark.ui
@pytest.mark.cart_ui
@allure.epic("小牛电商")
@allure.feature("购物车模块-ui")
class TestCartUi:

    @pytest.fixture(autouse=True)
    def init_page(self,driver,login):
        self.cart_page=CartPage(driver)
        self.product_page=ProductPage(driver)


    @allure.story("添加商品进入购物车并删除")
    @allure.title("添加商品id为: {product_id},名称为: '{product_name}'进入购物车")
    @pytest.mark.parametrize('product_id,product_name,add_times',csv_load(r'test_ui\data\cart.csv'))
    def test_add_product_to_cart(self,product_id,product_name,add_times):
        with allure.step("点击'加入购物车'按钮"):
            for p in range(int(add_times)):
                self.product_page.click_add_to_cart_button(product_name)
                toast=self.cart_page.get_toast()
                assert_with_log(toast=='已加入购物车',f"toast文案显示异常,预期: 已加入购物车,实际文案: {toast}")
                self.cart_page.wait_toast_invisible('已加入购物车')

                actual_quantity=self.cart_page.get_cart_item_quantity(product_name)
                assert_with_log(isinstance(actual_quantity,int) and actual_quantity>0,f"商品数量异常：{actual_quantity}")
                assert_with_log(self.cart_page.get_cart_item_quantity(product_name)==p+1,f"商品库存异常,预期库存: {p+1},实际库存: {actual_quantity}")

                price=float(self.product_page.get_product_price(product_name))
                subtotal_text=self.cart_page.get_cart_item_subtotal_text(product_name)
                assert_with_log(self.cart_page.is_cart_item_subtotal_two_decimals(product_name) and price>0,f"商品小计异常: {subtotal_text},应为保留两位小数的正数")

                cart_count=int(self.cart_page.get_cart_count_text())
                assert_with_log(cart_count==p+1,f"购物车商品数量统计异常,预期: {p+1},实际库存: {cart_count}")

            assert_with_log(self.cart_page.get_cart_item_remove_button(product_name).is_enabled(),f"{product_name}对应'删除'按钮不可用")

            subtotal=self.cart_page.get_cart_item_subtotal(product_name)
            assert_with_log(price*actual_quantity==subtotal,f"商品小计异常")

            name=self.cart_page.get_cart_item_name(product_id=product_id)
            assert_with_log(name==product_name,f"商品名称显示异常,预期名称: {product_name},实际名称: {name}")

            with allure.step("删除购物车商品"):
                self.cart_page.click_remove_cart_button(product_name)

            toast=self.cart_page.get_toast()
            assert_with_log(toast=='已删除购物车商品',f"toast文案显示异常,预期: 已删除购物车商品,实际文案: {toast}")
            # 删除是异步的:toast先出现,购物车统计随后刷新,必须等刷新完成再断言
            expect_cart_count=cart_count-actual_quantity
            self.cart_page.wait_for_cart_count_text(expect_cart_count)
            after_cart_count=int(self.cart_page.get_cart_count_text())
            assert_with_log(after_cart_count==expect_cart_count,f"删除商品时,购物车商品数量统计错误,预期: {expect_cart_count},实际: {after_cart_count}")



    @allure.story("查询购物车")
    @allure.title("购物车为空时,查询购物车")
    def test_select_cart_when_empty(self):
        with allure.step("定位元素"):
            empty_cart_text=self.cart_page.get_cart_empty_text()

        assert_with_log(empty_cart_text=='购物车为空',f"购物车为空时,文案显示异常,预期文案: 购物车为空,实际文案: {empty_cart_text}")


    @allure.story("购物车ui检查")
    @allure.title("'创建订单'按钮检查")
    def test_create_order_button(self):
        with allure.step("定位'创建订单'按钮"):
            create_button_text=self.cart_page.get_create_order_button_text()
            create_button_is_enable=self.cart_page.create_order_button_is_enable()

        assert_with_log(create_button_text=='创建订单',f"'创建订单'按钮文案异常,预期文案:创建订单,实际文案:{create_button_text}")
        assert_with_log(create_button_is_enable,f"'创建订单'按钮不可用")


    
