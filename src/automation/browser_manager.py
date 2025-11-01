from playwright.sync_api import BrowserContext, Playwright
from config.settings import CHROME_PROFILE_DIR, VIEWPORT, USER_AGENT, LOCALE, TIMEZONE_ID

def make_persistent_chrome(p: Playwright) -> BrowserContext:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=str(CHROME_PROFILE_DIR),
        channel="chrome",
        headless=False,
        viewport=VIEWPORT,
        user_agent=USER_AGENT,
        locale=LOCALE,
        timezone_id=TIMEZONE_ID,
        args=[
            "--disable-blink-features=AutomationControlled",
            f"--window-size={VIEWPORT['width']},{VIEWPORT['height']}"
        ]
    )
    ctx.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
    return ctx
