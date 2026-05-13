"""
Update Time Dialog - Modal dialog hiển thị tiến độ cập nhật thời gian
"""

import threading
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QDialog,
)

from qfluentwidgets import (
    BodyLabel,
    CaptionLabel,
    PushButton,
    ProgressBar,
    TextEdit,
    FluentIcon,
    SubtitleLabel,
)

from src.riot_api import RiotAPIPool
from src.storage import AccountStorage
from src.models import Account
from datetime import datetime
from typing import List


class _Signals(QObject):
    progress = pyqtSignal(int, int, str)  # current, total, message
    log = pyqtSignal(str)
    finished = pyqtSignal(int, int)  # updated, errors


class UpdateTimeDialog(QDialog):
    """Modal dialog cập nhật thời gian chơi"""

    def __init__(self, accounts_to_update: List[Account], api_pool: RiotAPIPool, storage: AccountStorage, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cập nhật thời gian chơi")
        self.setMinimumSize(650, 500)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
            }
        """)

        self.accounts_to_update = accounts_to_update
        self.api_pool = api_pool
        self.storage = storage
        self.is_running = True

        # Signals
        self._signals = _Signals()
        self._signals.progress.connect(self._on_progress)
        self._signals.log.connect(self._on_log)
        self._signals.finished.connect(self._on_finished)

        self._init_ui()

        # Auto start
        self._start()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Header
        header = SubtitleLabel("🕐 Đang cập nhật thời gian chơi...")
        header.setStyleSheet("color: #ffffff;")
        layout.addWidget(header)

        # Info
        total = len(self.accounts_to_update)
        info = CaptionLabel(
            f"Cập nhật {total} tài khoản | {self.api_pool.key_count} API key(s) - tốc độ x{self.api_pool.key_count}"
        )
        info.setStyleSheet("color: #aaa;")
        layout.addWidget(info)

        # Progress bar
        self.progress_bar = ProgressBar(self)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Progress label
        self.progress_label = BodyLabel("Đang khởi tạo...")
        self.progress_label.setStyleSheet("color: #0078D4;")
        layout.addWidget(self.progress_label)

        # Log
        self.log_text = TextEdit(self)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet(
            "TextEdit { font-family: 'Consolas', monospace; font-size: 12px; "
            "color: #E0E0E0; background-color: #12121f; border: 1px solid #3d3d55; border-radius: 6px; }"
        )
        layout.addWidget(self.log_text)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.stop_btn = PushButton(FluentIcon.CLOSE, "Dừng")
        self.stop_btn.setStyleSheet("PushButton { color: #ffffff; }")
        self.stop_btn.clicked.connect(self._stop)
        btn_layout.addWidget(self.stop_btn)

        self.close_btn = PushButton(FluentIcon.ACCEPT, "Đóng")
        self.close_btn.setStyleSheet("PushButton { color: #ffffff; }")
        self.close_btn.setEnabled(False)
        self.close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.close_btn)

        layout.addLayout(btn_layout)

    def _start(self):
        """Bắt đầu update trong background thread"""
        self._signals.log.emit(f"🚀 Bắt đầu cập nhật {len(self.accounts_to_update)} tài khoản...")
        self._signals.log.emit(f"🔑 Sử dụng {self.api_pool.key_count} API key(s)\n")

        thread = threading.Thread(target=self._worker, daemon=True)
        thread.start()

    def _stop(self):
        """Dừng update"""
        self.is_running = False
        self._signals.log.emit("\n⏹ Đã dừng bởi người dùng.")
        self.stop_btn.setEnabled(False)

    def _worker(self):
        """Worker thread"""
        all_accounts = self.storage.load()

        # Map id_game -> index
        id_to_index = {}
        for i, acc in enumerate(all_accounts):
            if acc.id_game:
                id_to_index[acc.id_game] = i

        updated = 0
        errors = 0
        total = len(self.accounts_to_update)

        for idx, acc in enumerate(self.accounts_to_update, 1):
            if not self.is_running:
                break

            self._signals.log.emit(f"[{idx}/{total}] {acc.id_game}")

            try:
                lol_time, tft_time = self.api_pool.get_last_match_times(acc.id_game)

                account_idx = id_to_index.get(acc.id_game)
                if account_idx is not None:
                    if lol_time:
                        all_accounts[account_idx].last_match_time = lol_time
                        self._signals.log.emit(f"  ✓ LOL: {lol_time}")
                    else:
                        all_accounts[account_idx].last_match_time = "Không có"
                        self._signals.log.emit(f"  ✗ LOL: Không tìm thấy")

                    if tft_time:
                        all_accounts[account_idx].last_tft_time = tft_time
                        self._signals.log.emit(f"  ✓ TFT: {tft_time}")
                    else:
                        all_accounts[account_idx].last_tft_time = "Không có"
                        self._signals.log.emit(f"  ✗ TFT: Không tìm thấy")

                    all_accounts[account_idx].last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    updated += 1

            except Exception as e:
                self._signals.log.emit(f"  ❌ Lỗi: {str(e)}")
                errors += 1

            self._signals.progress.emit(idx, total, f"{idx}/{total} - {acc.id_game}")

        # Lưu
        if updated > 0:
            self.storage.save(all_accounts)
            self._signals.log.emit(f"\n💾 Đã lưu dữ liệu.")

        self._signals.finished.emit(updated, errors)

    def _on_progress(self, current: int, total: int, msg: str):
        pct = int((current / total) * 100)
        self.progress_bar.setValue(pct)
        self.progress_label.setText(msg)

    def _on_log(self, message: str):
        self.log_text.append(message)
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _on_finished(self, updated: int, errors: int):
        self.is_running = False
        self.progress_bar.setValue(100)
        self.progress_label.setText(f"✅ Hoàn thành! Cập nhật: {updated} | Lỗi: {errors}")
        self.progress_label.setStyleSheet("color: #40C057;")
        self.stop_btn.setEnabled(False)
        self.close_btn.setEnabled(True)
        self._signals.log.emit(f"\n🎉 Hoàn thành! Cập nhật: {updated} | Lỗi: {errors}")

    def closeEvent(self, event):
        """Ngăn đóng khi đang chạy"""
        if self.is_running:
            self._stop()
        event.accept()
