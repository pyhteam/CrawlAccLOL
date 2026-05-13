"""
Configuration module - Quản lý cấu hình ứng dụng
"""

import os
import json
from pathlib import Path


class AppConfig:
    """Cấu hình chung cho ứng dụng"""

    # Paths
    BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR = BASE_DIR / "data"
    ACCOUNTS_FILE = DATA_DIR / "accounts.json"
    CONFIG_FILE = DATA_DIR / "config.json"
    API_KEY_FILE = DATA_DIR / "riot_api_key.txt"

    # Crawl settings
    DEFAULT_PAGES = 6
    REQUEST_TIMEOUT = 30
    DELAY_BETWEEN_PAGES = 2.0
    DELAY_BETWEEN_SHOPS = 3.0
    RIOT_API_DELAY = 1.2

    # UI Settings
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 800
    WINDOW_MIN_WIDTH = 1024
    WINDOW_MIN_HEIGHT = 600

    # User Agent
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    @classmethod
    def ensure_dirs(cls):
        """Tạo các thư mục cần thiết"""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def load_user_config(cls) -> dict:
        """Load cấu hình người dùng"""
        if cls.CONFIG_FILE.exists():
            try:
                with open(cls.CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}

    @classmethod
    def save_user_config(cls, config: dict):
        """Lưu cấu hình người dùng"""
        cls.ensure_dirs()
        with open(cls.CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
