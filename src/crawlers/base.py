"""
Base Crawler - Lớp cơ sở cho tất cả các crawler
"""

import time
import requests
from abc import ABC, abstractmethod
from typing import List, Callable, Optional

from src.models import Account
from src.config import AppConfig


class BaseCrawler(ABC):
    """Lớp cơ sở cho các crawler"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": AppConfig.USER_AGENT})
        self._stop_flag = False

    @property
    @abstractmethod
    def shop_name(self) -> str:
        """Tên shop"""
        pass

    @property
    @abstractmethod
    def base_url(self) -> str:
        """URL gốc"""
        pass

    @abstractmethod
    def parse_page(self, html_content: str) -> List[Account]:
        """Parse HTML thành danh sách Account"""
        pass

    def get_page_url(self, page: int) -> str:
        """Tạo URL cho trang cụ thể"""
        return f"{self.base_url}?page={page}"

    def stop(self):
        """Dừng crawl"""
        self._stop_flag = True

    def reset(self):
        """Reset trạng thái"""
        self._stop_flag = False

    def crawl_page(self, page: int) -> List[Account]:
        """Crawl một trang"""
        url = self.get_page_url(page)

        try:
            response = self.session.get(url, timeout=AppConfig.REQUEST_TIMEOUT)
            response.raise_for_status()
            return self.parse_page(response.text)
        except requests.RequestException as e:
            print(f"[{self.shop_name}] Lỗi trang {page}: {e}")
            return []

    def crawl_all(
        self,
        max_pages: int = None,
        progress_callback: Optional[Callable[[int, int, int], None]] = None,
        log_callback: Optional[Callable[[str], None]] = None,
    ) -> List[Account]:
        """
        Crawl tất cả các trang

        Args:
            max_pages: Số trang tối đa
            progress_callback: Callback(current_page, total_pages, accounts_found)
            log_callback: Callback(message) để log
        """
        self.reset()
        max_pages = max_pages or AppConfig.DEFAULT_PAGES
        all_accounts: List[Account] = []

        def log(msg: str):
            if log_callback:
                log_callback(msg)
            else:
                print(msg)

        log(f"[{self.shop_name}] Bắt đầu crawl {max_pages} trang...")

        for page in range(1, max_pages + 1):
            if self._stop_flag:
                log(f"[{self.shop_name}] Đã dừng bởi người dùng.")
                break

            accounts = self.crawl_page(page)
            all_accounts.extend(accounts)

            log(f"[{self.shop_name}] Trang {page}/{max_pages}: {len(accounts)} tài khoản")

            if progress_callback:
                progress_callback(page, max_pages, len(all_accounts))

            # Delay giữa các trang
            if page < max_pages and not self._stop_flag:
                time.sleep(AppConfig.DELAY_BETWEEN_PAGES)

        log(f"[{self.shop_name}] Hoàn thành! Tổng: {len(all_accounts)} tài khoản")
        return all_accounts
