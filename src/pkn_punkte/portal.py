from __future__ import annotations

import random
import time
from contextlib import AbstractContextManager
from datetime import datetime
from pathlib import Path
from types import TracebackType

from playwright.sync_api import Page, sync_playwright

from .config import Config
from .loader import Entry
from .runlog import RunLog


class Portal(AbstractContextManager["Portal"]):
    def __init__(self, config: Config, runlog: RunLog, headless: bool = True) -> None:
        self._config = config
        self._runlog = runlog
        self._headless = headless
        self._pw = None
        self._browser = None
        self._context = None
        self.page: Page | None = None

    def __enter__(self) -> "Portal":
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(headless=self._headless)
        self._context = self._browser.new_context()
        self._context.set_default_timeout(self._config.timing.page_timeout_ms)
        self.page = self._context.new_page()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._context:
            self._context.close()
        if self._browser:
            self._browser.close()
        if self._pw:
            self._pw.stop()

    def _pause(self) -> None:
        t = self._config.timing
        time.sleep(random.uniform(t.min_action_delay_sec, t.max_action_delay_sec))

    def _screenshot(self, label: str) -> Path:
        out_dir = self._config.paths.screenshots_dir
        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = out_dir / f"{stamp}_{label}.png"
        assert self.page is not None
        self.page.screenshot(path=str(path), full_page=True)
        return path

    def login(self) -> None:
        assert self.page is not None
        sel = self._config.selectors.login
        creds = self._config.credentials
        self._runlog.write("login.start", url=self._config.portal.login_url)
        self.page.goto(self._config.portal.login_url)
        self._pause()
        self.page.fill(sel.username, creds.username)
        self._pause()
        self.page.fill(sel.password, creds.password)
        self._pause()
        self.page.click(sel.submit)
        if sel.success_marker:
            self.page.wait_for_selector(sel.success_marker)
        shot = self._screenshot("login")
        self._runlog.write("login.ok", screenshot=str(shot))

    def submit_entry(self, entry: Entry, *, dry_run: bool) -> None:
        assert self.page is not None
        sel = self._config.selectors.entry
        if not self._config.portal.entry_url:
            raise RuntimeError("portal.entry_url is not configured")
        if not all([sel.vnr, sel.date, sel.duration_minutes, sel.participant_efn, sel.submit]):
            raise RuntimeError(
                "entry selectors not fully configured — inspect the form in DevTools "
                "and fill selectors.entry in config.yaml"
            )

        self._runlog.write("entry.start", key=entry.key, dry_run=dry_run)
        self.page.goto(self._config.portal.entry_url)
        self._pause()

        self.page.fill(sel.vnr, self._config.vnr)
        self._pause()
        self.page.fill(sel.date, entry.session_date.isoformat())
        self._pause()
        self.page.fill(sel.duration_minutes, str(entry.duration_minutes))
        self._pause()
        self.page.fill(sel.participant_efn, entry.efn)
        if sel.participant_name:
            self._pause()
            self.page.fill(sel.participant_name, entry.name)

        before = self._screenshot(f"entry_{entry.key.replace('|', '_')}_filled")

        if dry_run:
            self._runlog.write("entry.dry_run", key=entry.key, screenshot=str(before))
            return

        self._pause()
        self.page.click(sel.submit)
        if sel.confirmation_marker:
            self.page.wait_for_selector(sel.confirmation_marker)
        after = self._screenshot(f"entry_{entry.key.replace('|', '_')}_confirmed")
        self._runlog.write("entry.ok", key=entry.key, screenshot=str(after))
