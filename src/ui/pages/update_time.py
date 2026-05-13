"""
Update Time Page - Cập nhật thời gian chơi gần nhất qua Riot API
"""

import threading
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
)

from qfluentwidgets import (
    ScrollArea,
    TitleLabel,
    CaptionLabel,
    BodyLabel,
    SubtitleLabel,
    CardWidget,
    PushButton,
    PrimaryPushButton,
    FluentIcon,
    ProgressBar,
    TextEdit,
    InfoBar,
    InfoBarPosition,
)

from src.riot_api import RiotAPI, RiotAPIPool
from src.storage import AccountStorage
from src.config import AppConfig
from src.models import Account
from datetime import datetime


class UpdateSignals(QObject):
    """Signals cho update thread"""
    progress = pyqtSignal(int, int, str)  # current, total, message
    log = pyqtSignal(str)
    finished = pyqtSignal(int, int)  # updated, errors
    error = pyqtSignal(str)


class UpdateTimePage(ScrollArea):
    """Trang cập nhật thời gian chơi gần nhất"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("updateTimePage")
        self.setWidgetResizable(True)
        self.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.is_updating = False
        self.signals = UpdateSignals()

        # Connect signals
        self.signals.progress.connect(self._on_progress)
        self.signals.log.connect(self._on_log)
        self.signals.finished.connect(self._on_finished)
        self.signals.error.connect(self._on_error)

        # Container
        self.container = QWidget()
        self.container.setStyleSheet("QWidget { background: transparent; }")
        self.setWidget(self.container)

        self.main_layout = QVBoxLayout(self.container)
        self.main_layout.setContentsMargins(36, 28, 36, 28)
        self.main_layout.setSpacing(20)

        self._init_header()
        self._init_info()
        self._init_controls()
        self._init_log()

        self.main_layout.addStretch()

    def _init_header(self):
        """Header"""
        title = TitleLabel("🕐 Cập nhật thời gian chơi")
        self.main_layout.addWidget(title)

        subtitle = CaptionLabel(
            "Sử dụng Riot API để cập nhật thời gian chơi LOL và TFT gần nhất cho tất cả tài khoản"
        )
        self.main_layout.addWidget(subtitle)

    def _init_info(self):
        """Info card"""
        info_card = CardWidget(self.container)
        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(20, 16, 20, 16)
        info_layout.setSpacing(8)

        info_items = [
            "• Cần có Riot API Key (cài đặt trong trang Cài đặt)",
            "• Hỗ trợ nhiều key để tăng tốc (N keys = tốc độ xN)",
            "• Mỗi tài khoản cần 3-5 API calls (resolve ID + LOL match + TFT match)",
            "• Rate limit mỗi key: 20 req/giây, 100 req/2 phút - tự động xử lý",
        ]

        for item in info_items:
            label = CaptionLabel(item)
            info_layout.addWidget(label)

        self.main_layout.addWidget(info_card)

    def _init_controls(self):
        """Controls"""
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(12)

        self.start_btn = PrimaryPushButton(FluentIcon.PLAY, "Bắt đầu cập nhật")
        self.start_btn.setFixedHeight(40)
        self.start_btn.setFixedWidth(200)
        self.start_btn.clicked.connect(self._start_update)
        controls_layout.addWidget(self.start_btn)

        self.stop_btn = PushButton(FluentIcon.CLOSE, "Dừng")
        self.stop_btn.setFixedHeight(40)
        self.stop_btn.setFixedWidth(120)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_update)
        controls_layout.addWidget(self.stop_btn)

        controls_layout.addStretch()

        self.progress_label = CaptionLabel("")
        controls_layout.addWidget(self.progress_label)

        self.main_layout.addLayout(controls_layout)

        # Progress bar
        self.progress_bar = ProgressBar(self.container)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setValue(0)
        self.main_layout.addWidget(self.progress_bar)

    def _init_log(self):
        """Log output"""
        section_label = SubtitleLabel("Log")
        self.main_layout.addWidget(section_label)

        self.log_text = TextEdit(self.container)
        self.log_text.setReadOnly(True)
        self.log_text.setFixedHeight(300)
        self.log_text.setStyleSheet(
            "TextEdit { font-family: 'Consolas', monospace; font-size: 12px; color: #E0E0E0; background-color: #1a1a2e; }"
        )
        self.main_layout.addWidget(self.log_text)

    def _start_update(self):
        """Bắt đầu cập nhật"""
        if self.is_updating:
            return

        # Kiểm tra API key pool
        api_pool = RiotAPIPool.load_from_file()
        if not api_pool:
            InfoBar.warning(
                "Chưa có API Key",
                "Vui lòng nhập Riot API Key trong trang Cài đặt",
                duration=4000,
                position=InfoBarPosition.TOP_RIGHT,
                parent=self.window(),
            )
            return

        # Kiểm tra có accounts không
        storage = AccountStorage()
        accounts = storage.load()
        if not accounts:
            InfoBar.warning(
                "Chưa có dữ liệu",
                "Vui lòng crawl dữ liệu trước",
                duration=3000,
                position=InfoBarPosition.TOP_RIGHT,
                parent=self.window(),
            )
            return

        # Lọc accounts có id_game
        accounts_with_id = [a for a in accounts if a.id_game and "#" in a.id_game]
        if not accounts_with_id:
            InfoBar.warning(
                "Không có tài khoản hợp lệ",
                "Cần tài khoản có ID Game dạng 'Name#Tag' để tra cứu",
                duration=4000,
                position=InfoBarPosition.TOP_RIGHT,
                parent=self.window(),
            )
            return

        self.is_updating = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.log_text.clear()

        self.signals.log.emit(
            f"🚀 Bắt đầu cập nhật {len(accounts_with_id)}/{len(accounts)} tài khoản có ID hợp lệ..."
        )
        self.signals.log.emit(
            f"🔑 Sử dụng {api_pool.key_count} API key(s) - tốc độ x{api_pool.key_count}"
        )

        # Start thread
        thread = threading.Thread(
            target=self._update_worker,
            args=(accounts, accounts_with_id, api_pool),
            daemon=True,
        )
        thread.start()

    def _stop_update(self):
        """Dừng cập nhật"""
        self.is_updating = False
        self.signals.log.emit("⏹ Đang dừng...")

    def _update_worker(self, all_accounts, accounts_to_update, api_pool: RiotAPIPool):
        """Worker thread"""
        try:
            updated = 0
            errors = 0
            total = len(accounts_to_update)

            # Tạo map để update nhanh
            id_to_index = {}
            for i, acc in enumerate(all_accounts):
                if acc.id_game and "#" in acc.id_game:
                    id_to_index[acc.id_game] = i

            for idx, acc in enumerate(accounts_to_update, 1):
                if not self.is_updating:
                    break

                self.signals.log.emit(f"\n[{idx}/{total}] {acc.id_game}")

                try:
                    lol_time, tft_time = api_pool.get_last_match_times(acc.id_game)

                    # Update account
                    account_idx = id_to_index.get(acc.id_game)
                    if account_idx is not None:
                        if lol_time:
                            all_accounts[account_idx].last_match_time = lol_time
                            self.signals.log.emit(f"  ✓ LOL: {lol_time}")
                        else:
                            all_accounts[account_idx].last_match_time = "Không có"
                            self.signals.log.emit(f"  ✗ LOL: Không tìm thấy")

                        if tft_time:
                            all_accounts[account_idx].last_tft_time = tft_time
                            self.signals.log.emit(f"  ✓ TFT: {tft_time}")
                        else:
                            all_accounts[account_idx].last_tft_time = "Không có"
                            self.signals.log.emit(f"  ✗ TFT: Không tìm thấy")

                        all_accounts[account_idx].last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        updated += 1

                except Exception as e:
                    self.signals.log.emit(f"  ❌ Lỗi: {str(e)}")
                    errors += 1

                # Update progress
                pct = int((idx / total) * 100)
                self.signals.progress.emit(pct, total, f"{idx}/{total}")

            # Lưu dữ liệu
            if updated > 0:
                storage = AccountStorage()
                storage.save(all_accounts)
                self.signals.log.emit(f"\n💾 Đã lưu dữ liệu.")

            self.signals.finished.emit(updated, errors)

        except Exception as e:
            self.signals.error.emit(str(e))

    def _on_progress(self, pct: int, total: int, msg: str):
        """Cập nhật progress"""
        self.progress_bar.setValue(pct)
        self.progress_label.setText(f"Đang xử lý: {msg}")

    def _on_log(self, message: str):
        """Thêm log"""
        self.log_text.append(message)
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _on_finished(self, updated: int, errors: int):
        """Hoàn thành"""
        self.is_updating = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setValue(100)

        self.signals.log.emit(
            f"\n🎉 Hoàn thành! Cập nhật: {updated} | Lỗi: {errors}"
        )

        # Refresh accounts page
        main_window = self.window()
        if hasattr(main_window, "accounts_page"):
            main_window.accounts_page._load_data()

        InfoBar.success(
            "Cập nhật hoàn thành",
            f"Đã cập nhật {updated} tài khoản",
            duration=4000,
            position=InfoBarPosition.TOP_RIGHT,
            parent=self.window(),
        )

    def _on_error(self, error_msg: str):
        """Lỗi"""
        self.is_updating = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        self.signals.log.emit(f"\n❌ Lỗi: {error_msg}")

        InfoBar.error(
            "Lỗi",
            error_msg,
            duration=5000,
            position=InfoBarPosition.TOP_RIGHT,
            parent=self.window(),
        )
