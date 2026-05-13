"""
Crawl Page - Trang crawl dữ liệu từ các shop
"""

import threading
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
)

from qfluentwidgets import (
    ScrollArea,
    TitleLabel,
    CaptionLabel,
    BodyLabel,
    CardWidget,
    PushButton,
    PrimaryPushButton,
    FluentIcon,
    ProgressBar,
    CheckBox,
    SpinBox,
    TextEdit,
    InfoBar,
    InfoBarPosition,
    SubtitleLabel,
)

from src.crawlers import ChothuesubCrawler, VnToolGameCrawler, ThueToolHayCrawler, ShopCTSCrawler
from src.storage import AccountStorage
from src.config import AppConfig


class CrawlSignals(QObject):
    """Signals cho crawl thread"""
    progress = pyqtSignal(int, int, int)  # current, total, accounts_found
    log = pyqtSignal(str)
    finished = pyqtSignal(int)  # total accounts crawled
    error = pyqtSignal(str)


class CrawlPage(ScrollArea):
    """Trang crawl dữ liệu"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("crawlPage")
        self.setWidgetResizable(True)

        self.is_crawling = False
        self.crawl_thread = None
        self.signals = CrawlSignals()

        # Connect signals
        self.signals.progress.connect(self._on_progress)
        self.signals.log.connect(self._on_log)
        self.signals.finished.connect(self._on_finished)
        self.signals.error.connect(self._on_error)

        # Container
        self.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.container = QWidget()
        self.container.setStyleSheet("QWidget { background: transparent; }")
        self.setWidget(self.container)

        self.main_layout = QVBoxLayout(self.container)
        self.main_layout.setContentsMargins(36, 28, 36, 28)
        self.main_layout.setSpacing(20)

        self._init_header()
        self._init_shop_selection()
        self._init_settings()
        self._init_controls()
        self._init_log()

        self.main_layout.addStretch()

    def _init_header(self):
        """Header"""
        title = TitleLabel("⬇️ Crawl dữ liệu")
        self.main_layout.addWidget(title)

        subtitle = CaptionLabel(
            "Chọn shop và cấu hình để bắt đầu crawl tài khoản LOL"
        )
        self.main_layout.addWidget(subtitle)

    def _init_shop_selection(self):
        """Chọn shop để crawl"""
        section_label = SubtitleLabel("Chọn Shop")
        self.main_layout.addWidget(section_label)

        shops_card = CardWidget(self.container)
        shops_layout = QVBoxLayout(shops_card)
        shops_layout.setContentsMargins(20, 16, 20, 16)
        shops_layout.setSpacing(12)

        self.cb_chothuesub = CheckBox("chothuesub.com - Cho thuê sub LOL")
        self.cb_chothuesub.setChecked(True)
        shops_layout.addWidget(self.cb_chothuesub)

        self.cb_vntoolgame = CheckBox("thuetool.com - Acc Rác LMHT")
        self.cb_vntoolgame.setChecked(True)
        shops_layout.addWidget(self.cb_vntoolgame)

        self.cb_thuetoolhay = CheckBox("thuetoolhay.com - ThueToolHay")
        self.cb_thuetoolhay.setChecked(True)
        shops_layout.addWidget(self.cb_thuetoolhay)

        self.cb_shopcts = CheckBox("shopcts.pro - Acc Rác Liên Minh")
        self.cb_shopcts.setChecked(True)
        shops_layout.addWidget(self.cb_shopcts)

        self.main_layout.addWidget(shops_card)

    def _init_settings(self):
        """Cài đặt crawl"""
        section_label = SubtitleLabel("Cài đặt")
        self.main_layout.addWidget(section_label)

        settings_card = CardWidget(self.container)
        settings_layout = QHBoxLayout(settings_card)
        settings_layout.setContentsMargins(20, 16, 20, 16)
        settings_layout.setSpacing(20)

        # Số trang
        pages_layout = QVBoxLayout()
        pages_label = CaptionLabel("Số trang mỗi shop")
        pages_layout.addWidget(pages_label)

        self.pages_spin = SpinBox(self.container)
        self.pages_spin.setRange(1, 50)
        self.pages_spin.setValue(AppConfig.DEFAULT_PAGES)
        self.pages_spin.setFixedWidth(120)
        pages_layout.addWidget(self.pages_spin)

        settings_layout.addLayout(pages_layout)

        # Mode
        mode_layout = QVBoxLayout()
        mode_label = CaptionLabel("Chế độ lưu")
        mode_layout.addWidget(mode_label)

        self.cb_append = CheckBox("Thêm vào dữ liệu cũ (không trùng)")
        self.cb_append.setChecked(True)
        mode_layout.addWidget(self.cb_append)

        settings_layout.addLayout(mode_layout)
        settings_layout.addStretch()

        self.main_layout.addWidget(settings_card)

    def _init_controls(self):
        """Nút điều khiển"""
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(12)

        self.start_btn = PrimaryPushButton(FluentIcon.PLAY, "Bắt đầu Crawl")
        self.start_btn.setFixedHeight(40)
        self.start_btn.setFixedWidth(180)
        self.start_btn.clicked.connect(self._start_crawl)
        controls_layout.addWidget(self.start_btn)

        self.stop_btn = PushButton(FluentIcon.CLOSE, "Dừng")
        self.stop_btn.setFixedHeight(40)
        self.stop_btn.setFixedWidth(120)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_crawl)
        controls_layout.addWidget(self.stop_btn)

        controls_layout.addStretch()

        # Progress
        self.progress_label = CaptionLabel("")
        self.progress_label.setStyleSheet("color: #0078D4;")
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
        self.log_text.setFixedHeight(200)
        self.log_text.setStyleSheet(
            "TextEdit { font-family: 'Consolas', monospace; font-size: 12px; color: #E0E0E0; background-color: #1a1a2e; }"
        )
        self.main_layout.addWidget(self.log_text)

    def _start_crawl(self):
        """Bắt đầu crawl"""
        if self.is_crawling:
            return

        # Kiểm tra có chọn shop nào không
        shops_selected = []
        if self.cb_chothuesub.isChecked():
            shops_selected.append("chothuesub")
        if self.cb_vntoolgame.isChecked():
            shops_selected.append("vntoolgame")
        if self.cb_thuetoolhay.isChecked():
            shops_selected.append("thuetoolhay")
        if self.cb_shopcts.isChecked():
            shops_selected.append("shopcts")

        if not shops_selected:
            InfoBar.warning(
                "Chưa chọn shop",
                "Vui lòng chọn ít nhất một shop để crawl",
                duration=3000,
                position=InfoBarPosition.TOP_RIGHT,
                parent=self.window(),
            )
            return

        self.is_crawling = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.log_text.clear()

        max_pages = self.pages_spin.value()
        append_mode = self.cb_append.isChecked()

        # Start crawl thread
        self.crawl_thread = threading.Thread(
            target=self._crawl_worker,
            args=(shops_selected, max_pages, append_mode),
            daemon=True,
        )
        self.crawl_thread.start()

    def _stop_crawl(self):
        """Dừng crawl"""
        self.is_crawling = False
        # Stop all crawlers
        self.signals.log.emit("⏹ Đang dừng...")

    def _crawl_worker(self, shops: list, max_pages: int, append_mode: bool):
        """Worker thread thực hiện crawl"""
        try:
            all_accounts = []
            crawlers = []

            if "chothuesub" in shops:
                crawlers.append(ChothuesubCrawler())
            if "vntoolgame" in shops:
                crawlers.append(VnToolGameCrawler())
            if "thuetoolhay" in shops:
                crawlers.append(ThueToolHayCrawler())
            if "shopcts" in shops:
                crawlers.append(ShopCTSCrawler())

            total_steps = len(crawlers) * max_pages
            current_step = 0

            for crawler in crawlers:
                if not self.is_crawling:
                    break

                def progress_cb(page, total, found):
                    nonlocal current_step
                    current_step += 1
                    progress_pct = int((current_step / total_steps) * 100)
                    self.signals.progress.emit(progress_pct, total_steps, found)

                def log_cb(msg):
                    self.signals.log.emit(msg)

                accounts = crawler.crawl_all(
                    max_pages=max_pages,
                    progress_callback=progress_cb,
                    log_callback=log_cb,
                )
                all_accounts.extend(accounts)

                if not self.is_crawling:
                    crawler.stop()
                    break

            # Lưu dữ liệu
            if all_accounts:
                storage = AccountStorage()
                if append_mode:
                    added = storage.append(all_accounts)
                    self.signals.log.emit(
                        f"\n✅ Đã thêm {added} tài khoản mới (bỏ qua trùng lặp)"
                    )
                else:
                    storage.save(all_accounts)
                    self.signals.log.emit(
                        f"\n✅ Đã lưu {len(all_accounts)} tài khoản"
                    )

            self.signals.finished.emit(len(all_accounts))

        except Exception as e:
            self.signals.error.emit(str(e))

    def _on_progress(self, progress_pct: int, total: int, found: int):
        """Cập nhật progress"""
        self.progress_bar.setValue(progress_pct)
        self.progress_label.setText(f"Đã tìm thấy: {found} tài khoản")

    def _on_log(self, message: str):
        """Thêm log message"""
        self.log_text.append(message)
        # Auto scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _on_finished(self, total: int):
        """Khi crawl hoàn thành"""
        self.is_crawling = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setValue(100)

        self.signals.log.emit(f"\n🎉 Hoàn thành! Tổng cộng: {total} tài khoản")

        # Refresh dashboard & accounts page
        main_window = self.window()
        if hasattr(main_window, "dashboard_page"):
            main_window.dashboard_page.refresh_data()
        if hasattr(main_window, "accounts_page"):
            main_window.accounts_page._load_data()

        InfoBar.success(
            "Crawl hoàn thành",
            f"Đã crawl được {total} tài khoản",
            duration=4000,
            position=InfoBarPosition.TOP_RIGHT,
            parent=self.window(),
        )

    def _on_error(self, error_msg: str):
        """Khi có lỗi"""
        self.is_crawling = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        self.signals.log.emit(f"\n❌ Lỗi: {error_msg}")

        InfoBar.error(
            "Lỗi crawl",
            error_msg,
            duration=5000,
            position=InfoBarPosition.TOP_RIGHT,
            parent=self.window(),
        )
