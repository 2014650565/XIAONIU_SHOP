import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import allure
from common.assert_util import assert_with_log
import logging
from test_ui.pages.product_page import ProductPage
from common.csv_util import csv_load
import logging
import re

log=logging.getLogger(__name__)

@pytest.mark.product_ui
@pytest.mark.ui
@allure.epic("小牛电商")
@allure.feature("商品模块-ui")
class TestProductUi():

    @pytest.fixture(autouse=True)
    def init_page(self,driver,api_client):
        self.page=ProductPage(driver)
        self.api_client=api_client

    @pytest.mark.usefixtures("login")
    @allure.story("商品ui检查")
    @allure.title("{product_name}商品ui检查")
    @pytest.mark.parametrize('product_name,product_description,product_price,product_stock,button_enable',csv_load(r"test_ui\data\product.csv"))
    def test_select_product(self,product_name,product_description,product_price,product_stock,button_enable):
        with allure.step("从商品页面获取数据"):
            actual_name=self.page.get_product_name(product_name)
            actual_stock=self.page.get_product_stock(product_name)[3:]
            actual_price=self.page.get_product_price(product_name)[1:]
            actual_description=self.page.get_product_desciption(product_name)
            add_cart_text=self.page.get_add_cart_button_text(product_name)
            add_cart_is_enable=self.page.add_to_cart_button_is_enable(product_name)
            log.info(f"商品名称:{actual_name},库存:{actual_stock},价格:{actual_price},介绍:{actual_description}")

        assert_with_log(actual_name==product_name,f"商品名称异常,预期名称: {product_name}, 实际名称: {actual_name}")
        assert_with_log(actual_description==product_description,f"商品描述异常,预期: {product_description}, 实际: {actual_description}")
        assert_with_log(float(actual_price)>0,f"商品价格异常,应为大于0保留两位小数的值,实际价格:{actual_price}")
        assert_with_log(actual_price==product_price,f"商品价格异常,预期: {product_price}, 实际: {actual_price}")
        #断言价格是否保留两位小数
        assert_with_log(
            re.fullmatch(r"\d+\.\d{2}",actual_price) is not None,
            f"价格未保留两位小数,实际价格:{actual_price}")
        #断言库存非负整数
        assert_with_log(actual_stock.isdigit() and int(actual_stock)>=0, f"库存应为非负整数,实际库存:{actual_stock}")
        assert_with_log(actual_stock==product_stock,f"商品库存异常,预期: {product_stock}, 实际: {actual_stock}")

        assert_with_log(add_cart_text=='加入购物车',f"'加入购物车'文案异常,实际文案:{add_cart_text}")
        assert_with_log(str(add_cart_is_enable)==button_enable,f"商品对应的'加入购物车'按钮与预期不符")


    @allure.story("商品ui检查")
    @allure.title("'刷新商品'检查")
    @pytest.mark.usefixtures("login")
    def test_refresh_button(self,add_products_to_cart):
        with allure.step("获取'刷新商品'按钮信息"):
            refresh_button_text=self.page.get_refresh_button_text()
            refresh_button_is_enable=self.page.get_refresh_button_is_enable()

        assert_with_log(refresh_button_text=='刷新商品',f"'刷新商品'文案有误, 实际文案: {refresh_button_text}")
        assert_with_log(refresh_button_is_enable,"'刷新商品'按钮不可用")

        with allure.step("记录刷新前各商品库存"):
            pre_quantity={p['productName']: int(self.page.get_product_stock(p["productName"])[3:])
                          for p in add_products_to_cart}

        with allure.step("通过接口创建订单,扣减库存"):
            self.api_client.post(path='orders')

        with allure.step("点击刷新按钮,校验库存已更新"):
            self.page.click_refresh_button()
            for p in add_products_to_cart:
                product_name=p["productName"]
                expect_quantity=pre_quantity[product_name]-p['quantity']
                WebDriverWait(self.page.driver,5).until(lambda _: int(self.page.get_product_stock(product_name)[3:])==expect_quantity,
                                                        message=f"等待商品'{product_name}'库存变为{expect_quantity}超时")
                after_quantity = int(self.page.get_product_stock(p["productName"])[3:])
                assert_with_log(after_quantity==expect_quantity, f"商品'{product_name}'刷新有误, 预期库存: {expect_quantity}, 实际库存: {after_quantity}")
