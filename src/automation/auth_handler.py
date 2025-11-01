import os
from playwright.sync_api import BrowserContext, Page
from config.settings import GEMINI_URL
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
    page.goto("https://accounts.google.com/", timeout=30_000)
    page.wait_for_timeout(2000)
    if "accounts.google.com" in page.url:
        login_google(page)
    page.goto(GEMINI_URL, timeout=30_000)

    page_ready_btn = page.get_by_role("button", name=L.RE_DEEP_RESEARCH)
    page_ready_btn.wait_for(state="visible", timeout=30_000)

    return page
