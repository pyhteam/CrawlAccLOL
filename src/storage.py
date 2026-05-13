"""
Storage module - Quản lý lưu trữ dữ liệu JSON
"""

import json
import shutil
from pathlib import Path
from typing import List
from datetime import datetime

from src.models import Account
from src.config import AppConfig


class AccountStorage:
    """Quản lý lưu trữ tài khoản vào JSON"""

    def __init__(self, file_path: Path = None):
        self.file_path = file_path or AppConfig.ACCOUNTS_FILE
        AppConfig.ensure_dirs()

    def load(self) -> List[Account]:
        """Load danh sách tài khoản từ file JSON"""
        if not self.file_path.exists():
            return []

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                return [Account.from_dict(item) for item in data]
        except (json.JSONDecodeError, IOError, TypeError) as e:
            print(f"[Storage] Lỗi đọc file: {e}")

        return []

    def save(self, accounts: List[Account]):
        """Lưu danh sách tài khoản vào file JSON"""
        AppConfig.ensure_dirs()

        # Backup file cũ trước khi ghi
        if self.file_path.exists():
            backup_path = self.file_path.with_suffix(".json.bak")
            try:
                shutil.copy2(self.file_path, backup_path)
            except IOError:
                pass

        data = [acc.to_dict() for acc in accounts]

        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_count(self) -> int:
        """Đếm số tài khoản trong file"""
        accounts = self.load()
        return len(accounts)

    def append(self, new_accounts: List[Account]):
        """Thêm tài khoản mới vào file (không trùng lặp)"""
        existing = self.load()
        existing_links = {acc.link for acc in existing if acc.link}

        added = 0
        for acc in new_accounts:
            if acc.link and acc.link not in existing_links:
                existing.append(acc)
                existing_links.add(acc.link)
                added += 1
            elif not acc.link:
                existing.append(acc)
                added += 1

        self.save(existing)
        return added

    def clear(self):
        """Xóa toàn bộ dữ liệu"""
        self.save([])

    def export_summary(self) -> dict:
        """Xuất thống kê tổng quan"""
        accounts = self.load()
        if not accounts:
            return {"total": 0}

        # Thống kê theo shop
        shop_stats = {}
        rank_stats = {}
        prices = []

        for acc in accounts:
            shop = acc.shop or "Unknown"
            shop_stats[shop] = shop_stats.get(shop, 0) + 1

            rank = acc.rank or "Unknown"
            rank_stats[rank] = rank_stats.get(rank, 0) + 1

            if acc.price_numeric > 0:
                prices.append(acc.price_numeric)

        return {
            "total": len(accounts),
            "shops": shop_stats,
            "ranks": rank_stats,
            "price_min": min(prices) if prices else 0,
            "price_max": max(prices) if prices else 0,
            "price_avg": int(sum(prices) / len(prices)) if prices else 0,
        }
