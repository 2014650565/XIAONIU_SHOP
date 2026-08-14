import platform
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support.ui import WebDriverWait

# CI network probe: reproduce browser-side /api requests and print per-request
# timing plus page state. Used to find out which layer (DNS / domain / server /
# Chrome) causes UI test timeouts on GitHub Actions.

BASE_URL = "http://ceshixiaoniu.com/ecommerce-practice-app.html"
USERNAME = "tester"
PASSWORD = "123456"


def api_timings(driver):
    # Collect completed /api requests via the Performance API (ms).
    return driver.execute_script(
        "return performance.getEntriesByType('resource')"
        ".filter(e => e.name.includes('/api/'))"
        ".map(e => ({url: e.name, start_ms: Math.round(e.startTime), duration_ms: Math.round(e.duration)}))"
    )


def page_state(driver):
    def text(css):
        try:
            return driver.find_element(By.CSS_SELECTOR, css).text
        except Exception:
            return "<missing>"

    return {
        "toast": text("#toast"),
        "productCount": text("#productCount"),
        "cartCount": text("#cartCount"),
        "orderCount": text("#orderCount"),
        "productCards": len(driver.find_elements(By.CSS_SELECTOR, "#products .product-card")),
        "cartItems": len(driver.find_elements(By.CSS_SELECTOR, "#cart .cart-item")),
        "orderCards": len(driver.find_elements(By.CSS_SELECTOR, "#orders .order-card")),
    }


def new_driver():
    if platform.system() == "Windows":
        options = EdgeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        return webdriver.Edge(options=options)
    options = ChromeOptions()
    for arg in ("--headless=new", "--no-sandbox", "--disable-dev-shm-usage", "--window-size=1920,1080"):
        options.add_argument(arg)
    return webdriver.Chrome(options=options)


def main():
    driver = new_driver()
    driver.set_page_load_timeout(30)
    driver.set_script_timeout(15)
    try:
        t0 = time.time()
        driver.get(BASE_URL)
        print(f"[probe] page load: {time.time() - t0:.2f}s", flush=True)

        user = driver.find_element(By.ID, "username")
        user.clear()
        user.send_keys(USERNAME)
        pwd = driver.find_element(By.ID, "password")
        pwd.clear()
        pwd.send_keys(PASSWORD)

        t0 = time.time()
        driver.find_element(By.ID, "loginBtn").click()
        time.sleep(5)
        print(f"[probe] login + 5s: elapsed={time.time() - t0:.2f}s state={page_state(driver)}", flush=True)
        print(f"[probe] api timings after login: {api_timings(driver)}", flush=True)

        t0 = time.time()
        try:
            status = driver.execute_async_script(
                "const done = arguments[arguments.length - 1];"
                "fetch('/api/health').then(r => done('status=' + r.status)).catch(e => done('error=' + e.message));"
            )
            print(f"[probe] fetch /api/health: {status} in {time.time() - t0:.2f}s", flush=True)
        except Exception as exc:
            print(f"[probe] fetch /api/health: TIMEOUT {exc!r} after {time.time() - t0:.2f}s", flush=True)

        try:
            btn = WebDriverWait(driver, 10).until(
                lambda d: d.find_element(By.CSS_SELECTOR, "[data-add-cart]")
            )
            btn.click()
            time.sleep(5)
            print(f"[probe] add-to-cart + 5s: state={page_state(driver)}", flush=True)
            print(f"[probe] api timings after add: {api_timings(driver)}", flush=True)
        except Exception as exc:
            print(f"[probe] add-to-cart failed: {exc!r}", flush=True)

        try:
            driver.find_element(By.ID, "createOrderBtn").click()
            time.sleep(3)
            print(f"[probe] create-order + 3s: state={page_state(driver)}", flush=True)
        except Exception as exc:
            print(f"[probe] create-order failed: {exc!r}", flush=True)

        try:
            driver.find_element(By.ID, "refreshOrders").click()
            time.sleep(5)
            print(f"[probe] refresh-orders + 5s: state={page_state(driver)}", flush=True)
            print(f"[probe] api timings after refresh-orders: {api_timings(driver)}", flush=True)
        except Exception as exc:
            print(f"[probe] refresh-orders failed: {exc!r}", flush=True)

        print("[probe] done", flush=True)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
