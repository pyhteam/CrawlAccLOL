"""
Data models - Định nghĩa cấu trúc dữ liệu
"""

from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime


@dataclass
class Account:
    """Model cho một tài khoản LOL"""

    id_game: str = ""
    rank: str = ""
    so_tuong: str = ""
    so_skin: str = ""
    gia: str = ""
    link: str = ""
    shop: str = ""
    account_id: str = ""
    level: str = ""
    last_match_time: str = ""
    last_tft_time: str = ""
    last_update: str = ""

    def to_dict(self) -> dict:
        """Chuyển sang dictionary, bỏ các field rỗng"""
        data = asdict(self)
        return {k: v for k, v in data.items() if v}

    @classmethod
    def from_dict(cls, data: dict) -> "Account":
        """Tạo Account từ dictionary"""
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)

    @property
    def price_numeric(self) -> int:
        """Lấy giá dạng số để sort/filter"""
        price_str = self.gia.replace("VNĐ", "").replace(",", "").replace(".", "").strip()
        try:
            return int(price_str)
        except (ValueError, TypeError):
            return 0

    @property
    def champions_count(self) -> int:
        """Số tướng dạng số"""
        try:
            return int(self.so_tuong)
        except (ValueError, TypeError):
            return 0

    @property
    def skins_count(self) -> int:
        """Số skin dạng số"""
        try:
            return int(self.so_skin)
        except (ValueError, TypeError):
            return 0
