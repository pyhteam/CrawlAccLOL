"""
CrawlAccLOL - Entry point
Chạy ứng dụng GUI chính
"""

import sys
import os
import io

# Fix encoding cho Windows console
if sys.stdout and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Đảm bảo import từ thư mục gốc
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from src.ui.main_window import MainWindow
from src.config import AppConfig


def main():
    """Entry point chính"""
    # Đảm bảo thư mục data tồn tại
    AppConfig.ensure_dirs()

    # Migrate dữ liệu cũ nếu có
    _migrate_old_data()

    # Khởi tạo Qt Application
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))

    # Tạo và hiển thị cửa sổ chính
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


def _migrate_old_data():
    """Migrate dữ liệu từ file cũ (all_accounts.json ở root) sang data/accounts.json"""
    import json

    old_file = AppConfig.BASE_DIR / "all_accounts.json"
    new_file = AppConfig.ACCOUNTS_FILE

    if old_file.exists() and not new_file.exists():
        try:
            AppConfig.ensure_dirs()
            # Copy dữ liệu
            with open(old_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            with open(new_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"[Migrate] Đã chuyển {len(data)} tài khoản sang {new_file}")
        except Exception as e:
            print(f"[Migrate] Lỗi: {e}")


if __name__ == "__main__":
    main()
