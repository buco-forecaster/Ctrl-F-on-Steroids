import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from playwright.sync_api import Page
from config import locators as L
from config.settings import DEFAULT_TIMEOUT_MS, DEFAULT_DEEP_RESEARCH_TIMEOUT_MS, DEFAULT_START_RESEARCH_TIMEOUT_MS


class GeminiClient:
    def __init__(self, page: Page):
        self.page = page

    # --- Client Methods START --- #
    def new_chat(self) -> None:
        new_chat_btn = self.page.locator('[aria-label="New chat"]')
        new_chat_btn.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
        new_chat_btn.click()
        time.sleep(2)

    def ask_followups(self, followups: List[str]) -> Dict[str, str]:
        answers = {}
        for q in followups or []:
            answers[q] = self.ask_and_capture(q)
        return answers

    def execute_deep_research(self, query: str) -> Optional[str]:
        start_btn = self.page.get_by_role("button", name=L.RE_DEEP_RESEARCH, exact=True)
        start_btn.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
        start_btn.click()

        box = self.page.get_by_role("textbox")
        box.click(timeout=DEFAULT_TIMEOUT_MS)
        box.fill(query, timeout=DEFAULT_TIMEOUT_MS)
        self.page.keyboard.press("Enter")

        btn = self.page.get_by_role("button", name=L.RE_START_RESEARCH, exact=True)
        btn.wait_for(state="visible", timeout=DEFAULT_START_RESEARCH_TIMEOUT_MS)
        time.sleep(1)
        btn.scroll_into_view_if_needed(timeout=DEFAULT_TIMEOUT_MS)
        btn.click(timeout=DEFAULT_TIMEOUT_MS)

        self.wait_for_answer(L.RE_COMPLETED, state="visible")

        return self.export_pdf(query=query)
        self.page.goto("https://gemini.google.com/app/da23344c7a5e47f7")
        return None

    # --- Client Methods END --- #

    def extract_last_assistant_answer(self) -> str:
        chat = self.page.locator(L.CHAT_CONTAINER).last
        chat.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)

        container = chat.locator(L.RESPONSE_CONTAINER).last
        container.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)

        msg = container.locator(L.MESSAGE_CONTENT).last
        if msg.count() > 0:
            return msg.inner_text().strip()
        return container.inner_text().strip()

    def wait_for_answer(self, text, state) -> None:
        just_sec = self.page.get_by_text(text).last
        just_sec.wait_for(state=state, timeout=DEFAULT_DEEP_RESEARCH_TIMEOUT_MS)
        time.sleep(1)

    def ask_and_capture(self, q: str) -> str:
        box = self.page.get_by_role("textbox")
        box.wait_for(state="attached", timeout=DEFAULT_TIMEOUT_MS)
        box.click(timeout=DEFAULT_TIMEOUT_MS)
        box.fill(q, timeout=DEFAULT_TIMEOUT_MS)
        self.page.keyboard.press("Enter")
        self.wait_for_answer(L.RE_FOLLOWUP_WAIT, state="visible")
        self.wait_for_answer(L.RE_FOLLOWUP_WAIT, state="hidden")
        return self.extract_last_assistant_answer()

    def export_pdf(self, query: Optional[str] = None) -> str:
        share_btn = self.page.get_by_role("button").filter(has_text=L.RE_SHARE_EXPORT).last
        share_btn.click(timeout=DEFAULT_TIMEOUT_MS)

        with self.page.expect_popup(timeout=DEFAULT_TIMEOUT_MS) as popup_info:
            menuitem = self.page.get_by_role("menuitem", name=L.RE_EXPORT_TO_DOCS)
            menuitem.click(timeout=DEFAULT_TIMEOUT_MS)
        time.sleep(5)

        doc_page = popup_info.value
        file_menu = doc_page.get_by_role("menuitem", name="File")
        file_menu.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
        file_menu.click(timeout=DEFAULT_TIMEOUT_MS)
        time.sleep(1)

        download_menu = doc_page.get_by_role("menuitem", name="Download")
        download_menu.hover(timeout=DEFAULT_TIMEOUT_MS)
        time.sleep(1)

        pdf_item = doc_page.get_by_role("menuitem", name="PDF Document")
        with doc_page.expect_download(timeout=DEFAULT_TIMEOUT_MS) as dl_info:
            pdf_item.click(timeout=DEFAULT_TIMEOUT_MS)

        download = dl_info.value
        out_path = self.save_as_pdf(query, download)
        doc_page.close()

        return out_path

    @staticmethod
    def save_as_pdf(query, downloaded_file) -> str:
        out_dir = "outputs"
        Path(out_dir).mkdir(exist_ok=True, parents=True)

        safe_query = (query or "export").strip().replace(" ", "_")[:34]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = f"{out_dir}/{timestamp}-{safe_query}.pdf"

        downloaded_file.save_as(out_path)
        return out_path
