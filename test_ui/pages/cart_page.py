import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from common.base_page import BasePage


class CartPage(BasePage):
    """购物车页面对象。

    购物车条目由前端 JS 动态渲染，每条 DOM 结构固定为：
        <div class="cart-item">
          <div>
            <strong>商品名称</strong>
            <div>数量：N · 小计：¥X.XX</div>
          </div>
          <button data-remove-cart="商品id">删除</button>
        </div>

    所以定位思路是：先用 #cart .cart-item 拿到所有条目，
    再按商品名（strong 文本）或删除按钮上的 data-remove-cart 值
    （商品 id）找到具体某一条，最后在条目内取名称、数量、小计和删除按钮。
    """

    def __init__(self, driver):
        super().__init__(driver)

    CART_CONTAINER = (By.ID, "cart")
    CART_ITEM = (By.CSS_SELECTOR, "#cart .cart-item")
    CART_ITEM_NAME = (By.XPATH, ".//strong")
    # 购物车条目内的信息行：数量：N · 小计：¥X.XX
    CART_ITEM_INFO = (By.XPATH, "./div/div")
    CART_REMOVE_BTN = (By.XPATH, ".//button[@data-remove-cart]")
    CREATE_ORDER_BTN = (By.ID, "createOrderBtn")
    CART_COUNT = (By.ID, "cartCount")
    CART_EMPTY_TEXT = "购物车为空"
    TOAST=(By.ID,'toast')

    def _cart_item_by_name(self, name):
        # 以购物车条目容器 .cart-item 为锚点，再按商品名找到对应条目
        locator = (
            By.XPATH,
            f"//div[contains(@class,'cart-item')]"
            f"[.//strong[normalize-space(.)='{name}']]",
        )
        return self.find(locator)

    def _cart_item_by_product_id(self, product_id):
        # data-remove-cart 的值就是商品 id，是页面留给自动化最稳定的钩子
        locator = (
            By.XPATH,
            f"//div[contains(@class,'cart-item')]"
            f"[.//button[@data-remove-cart='{product_id}']]",
        )
        return self.find(locator)

    def _cart_item(self, name=None, product_id=None):
        if name is None and product_id is None:
            raise ValueError("必须传入 name 或 product_id 之一")
        if product_id is not None:
            return self._cart_item_by_product_id(product_id)
        return self._cart_item_by_name(name)

    def get_cart_items(self):
        return self.driver.find_elements(*self.CART_ITEM)

    def get_cart_item_count(self):
        return len(self.get_cart_items())

    def wait_for_cart_item_count(self, count, timeout=5):
        WebDriverWait(self.driver, timeout).until(
            lambda d: len(d.find_elements(*self.CART_ITEM)) == count,
            message=f"等待购物车条目数变为 {count} 超时",
        )

    def get_cart_count_text(self):
        # 顶部统计数字：购物车所有商品数量之和
        return self.find(self.CART_COUNT).text

    def wait_for_cart_count_text(self, count, timeout=5):
        # 添加/删除商品后，购物车统计是异步刷新的，等待数字变为期望值再断言
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.find_element(*self.CART_COUNT).text == str(count),
            message=f"等待购物车商品数量统计变为 {count} 超时",
        )

    def get_cart_item_name(self, name=None, product_id=None):
        return self._cart_item(name=name, product_id=product_id).find_element(
            *self.CART_ITEM_NAME
        ).text

    def get_cart_item_remove_button(self, name=None, product_id=None):
        return self._cart_item(name=name, product_id=product_id).find_element(
            *self.CART_REMOVE_BTN
        )

    def get_cart_item_info(self, name=None, product_id=None):
        return self._cart_item(name=name, product_id=product_id).find_element(
            *self.CART_ITEM_INFO
        ).text

    def get_cart_item_quantity(self, name=None, product_id=None):
        text = self.get_cart_item_info(name=name, product_id=product_id)
        match = re.search(r"数量[:：]\s*(\d+)", text)
        if not match:
            raise AssertionError(f"无法从购物车条目中解析数量: {text}")
        return int(match.group(1))

    def get_cart_item_subtotal(self, name=None, product_id=None):
        text = self.get_cart_item_info(name=name, product_id=product_id)
        match = re.search(r"小计[:：]\s*¥([\d.]+)", text)
        if not match:
            raise AssertionError(f"无法从购物车条目中解析小计: {text}")
        return float(match.group(1))

    def get_cart_item_subtotal_text(self, name=None, product_id=None):
        # 返回信息行里“小计：¥199.00”的金额部分，即 ¥199.00
        text = self.get_cart_item_info(name=name, product_id=product_id)
        match = re.search(r"小计[:：]\s*(¥[\d.]+)", text)
        if not match:
            raise AssertionError(f"无法从购物车条目中解析小计: {text}")
        return match.group(1)

    def is_cart_item_subtotal_two_decimals(self, name=None, product_id=None):
        # 断言购物车小计保留两位小数，如 ¥199.00
        text = self.get_cart_item_subtotal_text(name=name, product_id=product_id)
        return re.fullmatch(r"¥\d+\.\d{2}", text) is not None

    def click_remove_cart_button(self, name=None, product_id=None):
        self.get_cart_item_remove_button(name=name, product_id=product_id).click()

    def is_cart_empty(self):
        return self.CART_EMPTY_TEXT in self.find(self.CART_CONTAINER).text

    def get_cart_empty_text(self):
        return self.find(self.CART_CONTAINER).text

    def click_create_order_button(self):
        self.click(self.CREATE_ORDER_BTN)

    def get_create_order_button_text(self):
        return self.find(self.CREATE_ORDER_BTN).text

    def create_order_button_is_enable(self):
        return self.find(self.CREATE_ORDER_BTN).is_enabled()
