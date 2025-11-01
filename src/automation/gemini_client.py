import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from playwright.sync_api import Page
from config import locators as L
from config.settings import DEFAULT_QUERY_TIMEOUT_MS, DEFAULT_RESEARCH_TIMEOUT_MS

class GeminiClient:
    def __init__(self, page: Page):
        self.page = page

    # --- Client Methods START --- #

    def ask_followups(self, followups: List[str]) -> Dict[str, str]:
        answers = {}
        for q in followups or []:
            answers[q] = self.ask_and_capture(q)
            #self.page.reload()
        return answers

    def execute_deep_research(self, query: str) -> Optional[str]:
        start_btn = self.page.get_by_role("button", name=L.RE_DEEP_RESEARCH, exact=True)
        start_btn.wait_for(state="visible", timeout=30_000)
        start_btn.click()

        box = self.page.get_by_role("textbox")
        box.click()
        box.fill(query)
        self.page.keyboard.press("Enter")

        btn = self.page.get_by_role("button", name=L.RE_START_RESEARCH, exact=True)
        btn.wait_for(state="visible", timeout=15_000)
        btn.scroll_into_view_if_needed(timeout=2000)
        btn.click(timeout=3000)

        self.wait_for_answer(L.RE_COMPLETED, state="visible")

        return self.export_to_pdf(query=query)
        self.page.goto("https://gemini.google.com/app/da23344c7a5e47f7")
        return None

    # --- Client Methods END --- #

    def extract_last_assistant_answer(self, timeout_ms: int = DEFAULT_QUERY_TIMEOUT_MS) -> str:
        chat = self.page.locator(L.CHAT_CONTAINER).last
        chat.wait_for(state="visible", timeout=timeout_ms)
        container = chat.locator(L.RESPONSE_CONTAINER).last
        container.wait_for(state="visible", timeout=timeout_ms)
        msg = container.locator(L.MESSAGE_CONTENT).last
        if msg.count() > 0:
            return msg.inner_text().strip()
        return container.inner_text().strip()

    def wait_for_answer(self, text, state) -> None:
        just_sec = self.page.get_by_text(text).last
        just_sec.wait_for(state=state, timeout=30_000)
        time.sleep(1)

    def ask_and_capture(self, q: str) -> str:
        box = self.page.get_by_role("textbox")
        box.click()
        box.fill(q)
        time.sleep(1)
        self.page.keyboard.press("Enter")
        time.sleep(3)

        self.wait_for_answer(L.RE_FOLLOWUP_WAIT, state="hidden")
        return self.extract_last_assistant_answer()

    def export_to_pdf(self, out_dir: str = "outputs", query: Optional[str] = None) -> str:
        dl_timeout = 90_000
        share_btn = self.page.get_by_role("button").filter(has_text=L.RE_SHARE_EXPORT).last
        share_btn.click()

        with self.page.expect_popup(timeout=dl_timeout) as popup_info:
            menuitem = self.page.get_by_role("menuitem", name=L.RE_EXPORT_TO_DOCS)
            menuitem.click()
        time.sleep(5)

        doc_page = popup_info.value
        file_menu = doc_page.get_by_role("menuitem", name="File")
        file_menu.wait_for(state="visible", timeout=dl_timeout)
        file_menu.click()

        download_menu = doc_page.get_by_role("menuitem", name="Download")
        download_menu.hover()

        pdf_item = doc_page.get_by_role("menuitem", name="PDF Document")
        with doc_page.expect_download(timeout=dl_timeout) as dl_info:
            pdf_item.click()
        download = dl_info.value

        Path(out_dir).mkdir(exist_ok=True, parents=True)
        safe_query = (query or "export").strip().replace(" ", "_")[:34]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = f"{out_dir}/{timestamp}-{safe_query}.pdf"
        download.save_as(out_path)
        doc_page.close()

        return out_path

