import json
import platform
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support.ui import WebDriverWait

# CI network probe: reproduce browser-side /api requests and diagnose why
# Selenium clicks on dashboard buttons may not trigger fetch calls in CI.

BASE_URL = "http://ceshixiaoniu.com/ecommerce-practice-app.html"
USERNAME = "tester"
PASSWORD = "123456"


def api_timings(driver):
    # Completed /api requests via the Performance API (ms).
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


def inject_instrumentation(driver):
    # Record every fetch call (even if it hangs) and every click (even if a
    # handler later stops propagation) so we can tell what the page received.
    driver.execute_script(
        """
        window.__probe_fetches = [];
        const origFetch = window.fetch.bind(window);
        window.fetch = function (url, options) {
            const rec = {url: String(url), method: (options && options.method) || 'GET',
                         started: Math.round(performance.now()), settled: null, status: null, error: null};
            window.__probe_fetches.push(rec);
            return origFetch(url, options).then(
                (r) => { rec.settled = Math.round(performance.now()); rec.status = r.status; return r; },
                (e) => { rec.settled = Math.round(performance.now()); rec.error = String(e); throw e; }
            );
        };
        window.__probe_clicks = [];
        document.addEventListener('click', (e) => {
            const t = e.target;
            window.__probe_clicks.push({
                t: Math.round(performance.now()),
                tag: t.tagName,
                id: t.id || '',
                cls: typeof t.className === 'string' ? t.className : '',
                x: Math.round(e.clientX), y: Math.round(e.clientY),
                trusted: e.isTrusted
            });
        }, true);
        """
    )


def dump_events(driver, label):
    data = json.loads(
        driver.execute_script(
            "return JSON.stringify({fetches: window.__probe_fetches, clicks: window.__probe_clicks});"
        )
    )
    print(f"[probe] {label}: state={page_state(driver)}", flush=True)
    print(f"[probe] {label}: fetches={data['fetches']}", flush=True)
    print(f"[probe] {label}: clicks={data['clicks']}", flush=True)
    print(f"[probe] {label}: api timings={api_timings(driver)}", flush=True)


def analyze_first_add_cart_button(driver):
    info = driver.execute_script(
        """
        const btn = document.querySelector('[data-add-cart]');
        if (!btn) return {found: false};
        btn.scrollIntoView({block: 'center'});
        const r = btn.getBoundingClientRect();
        const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
        const hit = document.elementFromPoint(cx, cy);
        const card = btn.closest('.product-card');
        const cs = getComputedStyle(btn);
        return {
            found: true,
            rect: {x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height)},
            disabled: btn.disabled,
            stockText: card ? (card.querySelector('.stock') || {textContent: null}).textContent : null,
            display: cs.display,
            visibility: cs.visibility,
            offsetParentNull: btn.offsetParent === null,
            hit: hit ? {tag: hit.tagName, id: hit.id || '', cls: typeof hit.className === 'string' ? hit.className : ''} : null,
            dashboardDisplay: getComputedStyle(document.querySelector('#dashboard')).display,
            loginPanelDisplay: getComputedStyle(document.querySelector('#loginPanel')).display,
            viewport: {w: window.innerWidth, h: window.innerHeight},
            visibilityState: document.visibilityState
        };
        """
    )
    print(f"[probe] add-cart button analysis: {info}", flush=True)


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
        print(
            f"[probe] browserVersion={driver.capabilities.get('browserVersion')} "
            f"platform={driver.capabilities.get('platformName')}",
            flush=True,
        )
        t0 = time.time()
        driver.get(BASE_URL)
        print(f"[probe] page load: {time.time() - t0:.2f}s", flush=True)

        inject_instrumentation(driver)

        user = driver.find_element(By.ID, "username")
        user.clear()
        user.send_keys(USERNAME)
        pwd = driver.find_element(By.ID, "password")
        pwd.clear()
        pwd.send_keys(PASSWORD)

        t0 = time.time()
        driver.find_element(By.ID, "loginBtn").click()
        time.sleep(5)
        print(f"[probe] login click + 5s: elapsed={time.time() - t0:.2f}s", flush=True)
        dump_events(driver, "after login")

        analyze_first_add_cart_button(driver)

        t0 = time.time()
        try:
            btn = WebDriverWait(driver, 10).until(
                lambda d: d.find_element(By.CSS_SELECTOR, "[data-add-cart]")
            )
            btn.click()
            time.sleep(5)
            print(f"[probe] selenium click add-cart + 5s: elapsed={time.time() - t0:.2f}s", flush=True)
            dump_events(driver, "after selenium add-cart click")
        except Exception as exc:
            print(f"[probe] selenium add-cart click raised: {exc!r}", flush=True)

        try:
            driver.execute_script("document.querySelector('[data-add-cart]').click();")
            time.sleep(3)
            print("[probe] js synthetic add-cart click + 3s", flush=True)
            dump_events(driver, "after js add-cart click")
        except Exception as exc:
            print(f"[probe] js add-cart click raised: {exc!r}", flush=True)

        t0 = time.time()
        try:
            driver.find_element(By.ID, "createOrderBtn").click()
            time.sleep(3)
            print(f"[probe] selenium click create-order + 3s: elapsed={time.time() - t0:.2f}s", flush=True)
            dump_events(driver, "after selenium create-order click")
        except Exception as exc:
            print(f"[probe] selenium create-order click raised: {exc!r}", flush=True)

        t0 = time.time()
        try:
            driver.find_element(By.ID, "refreshOrders").click()
            time.sleep(5)
            print(f"[probe] selenium click refresh-orders + 5s: elapsed={time.time() - t0:.2f}s", flush=True)
            dump_events(driver, "after selenium refresh-orders click")
        except Exception as exc:
            print(f"[probe] selenium refresh-orders click raised: {exc!r}", flush=True)

        print("[probe] done", flush=True)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
