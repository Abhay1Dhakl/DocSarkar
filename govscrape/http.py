import time
import requests
from typing import Optional

class HttpClient:
    def __init__(self, user_agent: str, timeout_sec: int, delay_sec: float):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})
        self.timeout_sec = timeout_sec
        self.delay_sec = delay_sec
        self._last_request_time: Optional[float] = None

    def _sleep_if_needed(self):
        if self._last_request_time is None:
            return
        elapsed = time.time() - self._last_request_time
        if elapsed < self.delay_sec:
            time.sleep(self.delay_sec - elapsed)

    def get_text(self, url: str) -> str:
        self._sleep_if_needed()
        r = self.session.get(url, timeout=self.timeout_sec)
        self._last_request_time = time.time()
        r.raise_for_status()
        return r.text

    def download_bytes(self, url: str) -> bytes:
        self._sleep_if_needed()
        r = self.session.get(url, timeout=self.timeout_sec)
        self._last_request_time = time.time()
        r.raise_for_status()
        return r.content
