from playwright.sync_api import sync_playwright, Page

import time
import re
from pathlib import Path
from datetime import datetime
import os

GEMINI_URL = "https://gemini.google.com/app"
AUTH_STATE_PATH = ".auth/storage_state_chrome.json"
CHROME_PROFILE_DIR = str(Path.home() / "chrome-automation-profile")

QUERY_DELIMITER = '---QUERY_SEPARATOR---'
FOLLOWUP_DELIMITER = '---FOLLOWUP_SEPARATOR---'

def read_queries_file(path="queries.txt"):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read().lstrip()
        defaults = None
        segments_part = text
        if text.startswith('---DEFAULT-FOLLOWUP---'):
            parts = text.split('---DEFAULT-FOLLOWUP---', 1)[1]
            first_split = parts.split(QUERY_DELIMITER, 1)
            defaults_block = first_split[0]
            segments_part = first_split[1] if len(first_split) > 1 else ''
            defaults = [chunk.strip() for chunk in defaults_block.strip().split(FOLLOWUP_DELIMITER) if chunk.strip()]
        segments = [s.strip() for s in segments_part.split(QUERY_DELIMITER) if s.strip()]
        result = []
        for seg in segments:
            if not seg:
                continue
            parts = [p.strip() for p in seg.split(FOLLOWUP_DELIMITER)]
            query = parts[0]
            followups = [p for p in parts[1:] if p]
            result.append({"query": query, "followups": followups})
        return (defaults, result)

def extract_last_assistant_answer(page: Page, timeout_ms: int = 60_000):
    # Scope to the latest chat container first, then continue as before
    chat = page.locator(".chat-container").last
    chat.wait_for(state="visible", timeout=timeout_ms)

    container = chat.locator("response-container").last
    container.wait_for(state="visible", timeout=timeout_ms)

    msg = container.locator("message-content").last
    if msg.count() > 0:
        return msg.inner_text().strip()
    return container.inner_text().strip()

def wait_for_research_complete(page: Page, timeout_ms: int = 10 * 60_000):
    """
    Waits for Deep Research to finish by polling multiple robust signals:
    1. "I've completed your research." message
    2. "Share & Export" button visible
    3. Both "Contents" and "Create" texts visible (not necessarily as buttons)
    Succeeds as soon as any is detected before timeout.
    """
    stop = time.time() + (timeout_ms / 1000)
    re_done = re.compile(r"I[’']ve\s+completed\s+your\s+research\.?", re.I)
    poll_interval = 2
    time.sleep(poll_interval)

    while True:
        try:
            # 1. Try for completion message
            done_txt = page.get_by_text(re_done)
            if done_txt.is_visible():
                return True
            done_txt.wait_for(state="visible", timeout=2000)
            return True
        except Exception:
            pass

        if time.time() > stop:
            raise TimeoutError("Timeout waiting for Deep Research completion signals.")
        time.sleep(poll_interval)

def wait_for_query_complete(page: Page, timeout_ms: int = 10 * 60_000):
    """
    Waits for Deep Research to finish by polling multiple robust signals:
    1. "I've completed your research." message
    2. "Share & Export" button visible
    3. Both "Contents" and "Create" texts visible (not necessarily as buttons)
    Succeeds as soon as any is detected before timeout.
    """
    stop = time.time() + (timeout_ms / 1000)
    re_done = re.compile(r"Just a sec\.\.\.", re.I)
    poll_interval = 2
    time.sleep(poll_interval)

    while True:
        try:
            # 1. Try for completion message
            done_txt = page.get_by_text(re_done)
            if not done_txt.is_visible():
                time.sleep(2)
                return True
            time.sleep(poll_interval)
        except Exception:
            pass

        if time.time() > stop:
            raise TimeoutError("Timeout waiting for Deep Research completion signals.")
        time.sleep(poll_interval)

def export_to_pdf_via_google_docs(page: Page, out_dir="outputs", query=None, dl_timeout=90_000):
    # Open "Share & Export" dropdown with robust toolbar selector
    share_text = re.compile(r"^\s*Share\s*&\s*Export\s*$", re.I)
    share_btn = page.get_by_role("button").filter(has_text=share_text).last
    share_btn.click()

    with page.expect_popup(timeout=dl_timeout) as popup_info:
        menuitem = page.get_by_role("menuitem", name=re.compile(r"Export\s+to\s+Docs", re.I))
        menuitem.click()

    time.sleep(8)  # Wait for popup to load
    doc_page = popup_info.value
    # Wait for Docs File menu to appear
    file_menu = doc_page.get_by_role("menuitem", name=re.compile(r"^File$", re.I))
    file_menu.wait_for(state="visible", timeout=dl_timeout)
    # Download as PDF through menu navigation
    file_menu.click()
    download_menu = doc_page.get_by_role("menuitem", name=re.compile(r"Download", re.I))
    download_menu.hover()
    pdf_item = doc_page.get_by_role("menuitem", name=re.compile(r"PDF\s+Document", re.I))
    with doc_page.expect_download(timeout=dl_timeout) as dl_info:
        pdf_item.click()
    download = dl_info.value
    # Build output path: outputs/YYYYMMDD_HHMMSS-queryslug.pdf
    Path(out_dir).mkdir(exist_ok=True, parents=True)
    safe_query = (query or "export").strip().replace(" ", "_")[:34]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = f"{out_dir}/{timestamp}-{safe_query}.pdf"
    download.save_as(out_path)
    # Optional: Close the Docs tab
    doc_page.close()
    return out_path

def ask_and_capture(page: Page, q: str):
    box = page.get_by_role("textbox")
    box.click()
    box.fill(q)
    page.keyboard.press("Enter")
    time.sleep(3)
    wait_for_query_complete(page)
    return extract_last_assistant_answer(page)

def simple_deep_research_flow(page: Page, query: str, followup_questions: list = None):
    # Trigger Deep Research as before
    start_btn = page.get_by_role("button", name=re.compile(r"Deep\s*Research", re.I))
    start_btn.wait_for(state="visible", timeout=30_000)
    start_btn.click()

    btn = page.locator(r'text=/\bDeep\s*Research\b/i').first
    btn.wait_for(state="visible", timeout=15_000)
    btn.scroll_into_view_if_needed(timeout=2000)
    btn.click(timeout=3000)

    box = page.get_by_role("textbox")
    box.click()
    box.fill(query)
    page.keyboard.press("Enter")

    # btn = page.locator(r'text=/\bStart\s*research\b/i').first
    # btn.wait_for(state="visible", timeout=60_000)
    # btn.scroll_into_view_if_needed(timeout=2000)
    # btn.click(timeout=3000)

    #wait_for_research_complete(page)
    #export_to_pdf_via_google_docs(page, out_dir="outputs", query=query)
    page.goto("https://gemini.google.com/app/7bef7336690c12a2")
    time.sleep(3)

    # Follow-up loop
    answers = {}
    if followup_questions:
        for follow in followup_questions:
            answers[follow] = ask_and_capture(page, follow)

    return answers

def make_persistent_chrome(p):
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=CHROME_PROFILE_DIR,
        channel="chrome",
        headless=False,
        viewport={"width": 2120, "height": 1080},
        user_agent=("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"),
        locale="en-US",
        timezone_id="Europe/Prague",
        args=[
            "--disable-blink-features=AutomationControlled",
            "--window-size=2120,1080"
        ]
    )
    ctx.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
    return ctx

def ensure_gemini_authenticated(ctx) -> Page:
    page = ctx.new_page()
    page.goto("https://accounts.google.com/", timeout=30_000)
    page.wait_for_timeout(2000)
    print("Navigated to Google Accounts for authentication.")

    if "accounts.google.com" in page.url:
        login_google(page)

    page.goto(GEMINI_URL, timeout=30_000)
    page.wait_for_timeout(2000)

    return page

def login_google(page: Page):
    email = os.environ.get("GOOGLE_EMAIL", None)
    password = os.environ.get("GOOGLE_PASSWORD", None)
    if not email or not password:
        print("GOOGLE_EMAIL and/or GOOGLE_PASSWORD environment variables not set.")
        input("Set those env vars and press ENTER to continue (or close to skip login).")
        return

    input()

import json

def save_answers_json(result, query, out_dir="outputs/answers"):
    Path(out_dir).mkdir(exist_ok=True, parents=True)
    def slug(s): return re.sub(r"[^a-zA-Z0-9_-]", "_", s)[:32]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"{ts}-{slug(query)}.json"
    payload = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "query": query,
        "followups": result
    }
    with open(f"{out_dir}/{fname}", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return f"{out_dir}/{fname}"

def open_gemini_chrome(url: str = GEMINI_URL, queries_file: str = "queries.txt"):
    auth_state_file = Path(AUTH_STATE_PATH)
    with sync_playwright() as p:
        ctx = make_persistent_chrome(p)
        try:
            page = ensure_gemini_authenticated(ctx)
            Path(AUTH_STATE_PATH).parent.mkdir(exist_ok=True, parents=True)
            ctx.storage_state(path=AUTH_STATE_PATH)
            print(f"Saved session state to {AUTH_STATE_PATH}")

            if queries_file and os.path.exists(queries_file):
                defaults, queries = read_queries_file(queries_file)
                results = []
                for segment in queries:
                    if segment["followups"]:
                        fups = segment["followups"]
                    elif defaults:
                        fups = defaults
                    res = simple_deep_research_flow(page, segment["query"], followup_questions=fups)
                    save_answers_json(res, segment["query"])
                    results.append({"query": segment["query"], **res})

                    # go to main page of gemini for next query
                    page.goto(url, timeout=30_000)
                    time.sleep(2)

                input("Press ENTER to close Chrome...")
                return results

            input("Press ENTER to close Chrome...")
            return None
        finally:
            ctx.close()
