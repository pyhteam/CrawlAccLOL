"""
Settings Page - Trang cài đặt
"""

from PyQt5.QtCore import Qt
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
    LineEdit,
    PushButton,
    PrimaryPushButton,
    FluentIcon,
    InfoBar,
    InfoBarPosition,
    SwitchButton,
    SpinBox,
)

from src.config import AppConfig
from src.riot_api import RiotAPI
from src import __version__


class SettingsPage(ScrollArea):
    """Trang cài đặt"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settingsPage")
        self.setWidgetResizable(True)
        self.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        # Container
        self.container = QWidget()
        self.container.setStyleSheet("QWidget { background: transparent; }")
        self.setWidget(self.container)

        self.main_layout = QVBoxLayout(self.container)
        self.main_layout.setContentsMargins(36, 28, 36, 28)
        self.main_layout.setSpacing(20)

        self._init_header()
        self._init_riot_api()
        self._init_crawl_settings()
        self._init_about()

        self.main_layout.addStretch()

    def _init_header(self):
        """Header"""
        title = TitleLabel("⚙️ Cài đặt")
        self.main_layout.addWidget(title)

        subtitle = CaptionLabel("Cấu hình ứng dụng và Riot API")
        self.main_layout.addWidget(subtitle)

    def _init_riot_api(self):
        """Riot API settings"""
        section_label = SubtitleLabel("Riot API")
        self.main_layout.addWidget(section_label)

        card = CardWidget(self.container)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 16, 20, 16)
        card_layout.setSpacing(12)

        # Description
        desc = CaptionLabel(
            "Nhập Riot API Key (mỗi dòng 1 key, nhiều key = tăng tốc cập nhật).\n"
            "Lấy key miễn phí tại: https://developer.riotgames.com/"
        )
        card_layout.addWidget(desc)

        # API Keys input (multi-line)
        from qfluentwidgets import TextEdit
        self.api_key_input = TextEdit(self.container)
        self.api_key_input.setPlaceholderText(
            "Nhập Riot API Key (mỗi dòng 1 key)...\n"
            "Ví dụ:\n"
            "RGAPI-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx\n"
            "RGAPI-yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"
        )
        self.api_key_input.setFixedHeight(120)

        # Load existing keys
        if AppConfig.API_KEY_FILE.exists():
            try:
                existing_keys = AppConfig.API_KEY_FILE.read_text().strip()
                if existing_keys:
                    self.api_key_input.setText(existing_keys)
            except IOError:
                pass

        card_layout.addWidget(self.api_key_input)

        # Save button + key count
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self.key_count_label = CaptionLabel("")
        self._update_key_count()
        btn_layout.addWidget(self.key_count_label)

        btn_layout.addStretch()

        save_key_btn = PrimaryPushButton(FluentIcon.SAVE, "Lưu Keys")
        save_key_btn.setFixedWidth(120)
        save_key_btn.clicked.connect(self._save_api_key)
        btn_layout.addWidget(save_key_btn)

        card_layout.addLayout(btn_layout)
        self.main_layout.addWidget(card)

    def _init_crawl_settings(self):
        """Crawl settings"""
        section_label = SubtitleLabel("Cài đặt Crawl")
        self.main_layout.addWidget(section_label)

        card = CardWidget(self.container)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 16, 20, 16)
        card_layout.setSpacing(16)

        # Delay between pages
        delay_layout = QHBoxLayout()
        delay_label = BodyLabel("Delay giữa các trang (giây)")
        delay_layout.addWidget(delay_label)
        delay_layout.addStretch()

        self.delay_spin = SpinBox(self.container)
        self.delay_spin.setRange(1, 10)
        self.delay_spin.setValue(int(AppConfig.DELAY_BETWEEN_PAGES))
        self.delay_spin.setFixedWidth(100)
        delay_layout.addWidget(self.delay_spin)
        card_layout.addLayout(delay_layout)

        # Request timeout
        timeout_layout = QHBoxLayout()
        timeout_label = BodyLabel("Request timeout (giây)")
        timeout_layout.addWidget(timeout_label)
        timeout_layout.addStretch()

        self.timeout_spin = SpinBox(self.container)
        self.timeout_spin.setRange(10, 120)
        self.timeout_spin.setValue(AppConfig.REQUEST_TIMEOUT)
        self.timeout_spin.setFixedWidth(100)
        timeout_layout.addWidget(self.timeout_spin)
        card_layout.addLayout(timeout_layout)

        # Save settings button
        save_layout = QHBoxLayout()
        save_layout.addStretch()
        save_settings_btn = PushButton(FluentIcon.SAVE, "Lưu cài đặt")
        save_settings_btn.clicked.connect(self._save_settings)
        save_layout.addWidget(save_settings_btn)
        card_layout.addLayout(save_layout)

        self.main_layout.addWidget(card)

    def _init_about(self):
        """About section"""
        section_label = SubtitleLabel("Thông tin")
        self.main_layout.addWidget(section_label)

        card = CardWidget(self.container)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 16, 20, 16)
        card_layout.setSpacing(8)

        info_items = [
            ("Ứng dụng", "CrawlAccLOL - Tool crawl tài khoản LOL"),
            ("Phiên bản", f"v{__version__}"),
            ("Framework", "PyQt5 + PyQt-Fluent-Widgets"),
            ("Tác giả", "SenMS"),
        ]

        for label, value in info_items:
            row = QHBoxLayout()
            row.addWidget(CaptionLabel(label))
            row.addStretch()
            row.addWidget(BodyLabel(value))
            card_layout.addLayout(row)

        self.main_layout.addWidget(card)

    def _save_api_key(self):
        """Lưu Riot API Keys"""
        text = self.api_key_input.toPlainText().strip()
        if not text:
            InfoBar.warning(
                "Chưa nhập key",
                "Vui lòng nhập ít nhất 1 Riot API Key",
                duration=3000,
                position=InfoBarPosition.TOP_RIGHT,
                parent=self.window(),
            )
            return

        # Lọc các dòng hợp lệ (bắt đầu bằng RGAPI-)
        keys = [k.strip() for k in text.splitlines() if k.strip()]
        valid_keys = [k for k in keys if k.startswith("RGAPI-")]

        if not valid_keys:
            InfoBar.warning(
                "Key không hợp lệ",
                "Key phải bắt đầu bằng 'RGAPI-'",
                duration=3000,
                position=InfoBarPosition.TOP_RIGHT,
                parent=self.window(),
            )
            return

        AppConfig.ensure_dirs()
        AppConfig.API_KEY_FILE.write_text("\n".join(valid_keys))
        self._update_key_count()

        InfoBar.success(
            "Đã lưu",
            f"Đã lưu {len(valid_keys)} API Key(s)",
            duration=3000,
            position=InfoBarPosition.TOP_RIGHT,
            parent=self.window(),
        )

    def _update_key_count(self):
        """Cập nhật hiển thị số key"""
        count = 0
        if AppConfig.API_KEY_FILE.exists():
            try:
                content = AppConfig.API_KEY_FILE.read_text().strip()
                keys = [k for k in content.splitlines() if k.strip().startswith("RGAPI-")]
                count = len(keys)
            except IOError:
                pass

        if count > 0:
            self.key_count_label.setText(f"🔑 {count} key(s) — tốc độ x{count}")
        else:
            self.key_count_label.setText("⚠️ Chưa có key")

    def _save_settings(self):
        """Lưu cài đặt crawl"""
        config = {
            "delay_between_pages": self.delay_spin.value(),
            "request_timeout": self.timeout_spin.value(),
        }
        AppConfig.save_user_config(config)

        # Update runtime config
        AppConfig.DELAY_BETWEEN_PAGES = float(self.delay_spin.value())
        AppConfig.REQUEST_TIMEOUT = self.timeout_spin.value()

        InfoBar.success(
            "Đã lưu",
            "Cài đặt đã được cập nhật",
            duration=3000,
            position=InfoBarPosition.TOP_RIGHT,
            parent=self.window(),
        )
