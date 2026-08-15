import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from common.base_page import BasePage


class OrderPage(BasePage):
    """订单页面对象。

    订单卡片由前端 JS 动态渲染，每张卡片 DOM 结构固定为：
        <article class="order-card">
          <div class="dashboard-head">
            <strong>订单号：1</strong>
            <span class="badge">待支付</span>
          </div>
          <p>金额：¥199.00 · 创建时间：2026/08/13 10:00:00</p>
          <ul>
            <li>接口自动化课程 × 1</li>
          </ul>
          <div class="order-actions">
            <button class="pay" data-pay-order="1">支付</button>
            <button class="cancel" data-cancel-order="1">取消</button>
          </div>
        </article>

    空订单时：#orders 的 class 变为 "orders empty"，文本为 "暂无订单"。

    定位思路和购物车一致：先拿 #orders .order-card 所有卡片，
    再按订单号（data-pay-order / data-cancel-order 的值）锁定某一张，
    最后在卡片内相对查找状态、金额、商品明细、支付/取消按钮。
    """

    def __init__(self, driver):
        super().__init__(driver)

    ORDER_CONTAINER = (By.ID, "orders")
    ORDER_CARD = (By.CSS_SELECTOR, "#orders .order-card")
    ORDER_ID = (By.XPATH, ".//div[contains(@class,'dashboard-head')]/strong")
    ORDER_STATUS = (By.XPATH, ".//span[contains(@class,'badge')]")
    ORDER_INFO = (By.XPATH, ".//p")
    ORDER_ITEMS = (By.XPATH, ".//ul/li")
    PAY_BTN = (By.XPATH, ".//button[contains(@class,'pay')]")
    CANCEL_BTN = (By.XPATH, ".//button[contains(@class,'cancel')]")
    REFRESH_BUTTON = (By.ID, "refreshOrders")
    ORDER_COUNT = (By.ID, "orderCount")
    TOAST=(By.ID,'toast')
    ORDER_EMPTY_TEXT = "暂无订单"

    def _order_card_by_id(self, order_id):
        # 订单号同时存在于支付/取消按钮的 data 属性上，是最稳定的钩子
        locator = (
            By.XPATH,
            f"//article[contains(@class,'order-card')]"
            f"[.//button[@data-pay-order='{order_id}']]",
        )
        return self.find(locator)

    def get_order_cards(self):
        return self.driver.find_elements(*self.ORDER_CARD)

    def get_order_ids(self):
        # 按页面显示顺序返回订单id列表
        cards = self.get_order_cards()
        return [card.find_element(*self.PAY_BTN).get_attribute("data-pay-order") for card in cards]

    def get_order_count_text(self):
        # 顶部订单统计数字：订单总数
        return int(self.find(self.ORDER_COUNT).text)

    def wait_for_order_count(self, count, timeout=20):
        # 创建/支付/取消订单后列表是异步刷新的，等待数量变为期望值再断言
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.find_element(*self.ORDER_COUNT).text == str(count),
            message=f"等待订单数量变为 {count} 超时",
        )

    def get_order_id(self, order_id):
        # 返回 "订单号：1" 形式的完整文本
        return self._order_card_by_id(order_id).find_element(*self.ORDER_ID).text

    def get_order_status(self, order_id):
        return self._order_card_by_id(order_id).find_element(*self.ORDER_STATUS).text

    def wait_for_order_status(self, order_id, expect_status, timeout=20):
        # 支付/取消后状态异步刷新，等待状态变为期望值再断言
        WebDriverWait(self.driver, timeout).until(
            lambda d: self.get_order_status(order_id) == expect_status,
            message=f"等待订单 {order_id} 状态变为 {expect_status} 超时",
        )

    def get_order_info(self, order_id):
        # 返回 "金额：¥199.00 · 创建时间：..." 的完整文本
        return self._order_card_by_id(order_id).find_element(*self.ORDER_INFO).text

    def get_order_amount_text(self, order_id):
        text = self.get_order_info(order_id)
        match = re.search(r"金额[:：]\s*(¥[\d.]+)", text)
        if not match:
            raise AssertionError(f"无法从订单中解析金额: {text}")
        return match.group(1)

    def get_order_amount(self, order_id):
        return float(self.get_order_amount_text(order_id).replace("¥", ""))

    def is_order_amount_two_decimals(self, order_id):
        # 断言订单金额保留两位小数，如 ¥199.00
        return re.fullmatch(r"¥\d+\.\d{2}", self.get_order_amount_text(order_id)) is not None

    def get_order_created_at(self, order_id):
        text = self.get_order_info(order_id)
        match = re.search(r"创建时间[:：]\s*([\d/: ]+)", text)
        if not match:
            raise AssertionError(f"无法从订单中解析创建时间: {text}")
        return match.group(1).strip()

    def get_order_items(self, order_id):
        # 返回商品明细列表，如 ["接口自动化课程 × 1"]
        card = self._order_card_by_id(order_id)
        return [li.text for li in card.find_elements(*self.ORDER_ITEMS)]

    def get_pay_button(self, order_id):
        return self._order_card_by_id(order_id).find_element(*self.PAY_BTN)

    def click_pay_button(self, order_id):
        btn = self.get_pay_button(order_id)
        self.driver.execute_script("arguments[0].click();", btn)

    def pay_button_is_enable(self, order_id):
        return self.get_pay_button(order_id).is_enabled()

    def get_cancel_button(self, order_id):
        return self._order_card_by_id(order_id).find_element(*self.CANCEL_BTN)

    def click_cancel_button(self, order_id):
        btn = self.get_cancel_button(order_id)
        self.driver.execute_script("arguments[0].click();", btn)

    def cancel_button_is_enable(self, order_id):
        return self.get_cancel_button(order_id).is_enabled()

    def get_order_empty_text(self):
        return self.find(self.ORDER_CONTAINER).text

    def is_orders_empty(self):
        return self.ORDER_EMPTY_TEXT in self.find(self.ORDER_CONTAINER).text

    def get_refresh_button_text(self):
        return self.find(self.REFRESH_BUTTON).text

    def refresh_button_is_enable(self):
        return self.find(self.REFRESH_BUTTON).is_enabled()

    def click_refresh_button(self):
        self.click(self.REFRESH_BUTTON)
