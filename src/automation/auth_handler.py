import os
import time

from playwright.sync_api import BrowserContext, Page
from config.settings import GEMINI_URL, GOOGLE_ACCOUNTS_URL, DEFAULT_TIMEOUT_MS, AUTH_STATE_PATH
from config import locators as L

def login_google(page: Page):
    email = os.environ.get("GOOGLE_EMAIL")
    password = os.environ.get("GOOGLE_PASSWORD")
    if not email or not password:
        input()
        return
    input()

def ensure_gemini_authenticated(ctx: BrowserContext) -> Page:
    page = ctx.new_page()
    page.goto(GOOGLE_ACCOUNTS_URL, timeout=DEFAULT_TIMEOUT_MS)
    page.wait_for_timeout(2000)
    if "accounts.google.com" in page.url:
        login_google(page)

    page.goto(GEMINI_URL)
    page_ready_btn = page.get_by_role("button", name=L.RE_DEEP_RESEARCH)
    page_ready_btn.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
    time.sleep(3)

    return page

def store_auth_state(ctx: BrowserContext):
    dir_path = os.path.dirname(AUTH_STATE_PATH)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    ctx.storage_state(path=AUTH_STATE_PATH)
