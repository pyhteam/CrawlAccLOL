"""
About Dialog - Popup thông tin tác giả khi mở app
"""

import webbrowser
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QDialog

from qfluentwidgets import (
    SubtitleLabel,
    BodyLabel,
    CaptionLabel,
    StrongBodyLabel,
    PrimaryPushButton,
    PushButton,
    FluentIcon,
    CardWidget,
)

from src import __version__, __app_name__, __author__, __facebook__, __zalo__


class AboutDialog(QDialog):
    """Popup thông tin tác giả"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thông tin")
        self.setFixedSize(480, 380)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
            }
        """)

        self._init_ui()

        # Không cho đóng trước 3 giây
        self._can_close = False
        QTimer.singleShot(3000, self._enable_close)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # App name
        title = SubtitleLabel(f"🎮 {__app_name__} v{__version__}")
        title.setStyleSheet("color: #ffffff; font-size: 18px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Description
        desc = CaptionLabel("Tool crawl và quản lý tài khoản LOL")
        desc.setStyleSheet("color: #aaa;")
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)

        # Author card
        card = CardWidget(self)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 16, 20, 16)
        card_layout.setSpacing(10)

        # Author
        author_row = QHBoxLayout()
        author_row.addWidget(BodyLabel("👤 Tác giả:"))
        author_row.addStretch()
        author_row.addWidget(StrongBodyLabel(__author__))
        card_layout.addLayout(author_row)

        # Zalo
        zalo_row = QHBoxLayout()
        zalo_row.addWidget(BodyLabel("📱 Zalo:"))
        zalo_row.addStretch()
        zalo_row.addWidget(StrongBodyLabel(__zalo__))
        card_layout.addLayout(zalo_row)

        # Facebook
        fb_row = QHBoxLayout()
        fb_row.addWidget(BodyLabel("🌐 Facebook:"))
        fb_row.addStretch()
        from qfluentwidgets import HyperlinkLabel
        fb_link = HyperlinkLabel("facebook.com/senms9x")
        fb_link.setUrl(__facebook__)
        fb_row.addWidget(fb_link)
        card_layout.addLayout(fb_row)

        layout.addWidget(card)

        # Ad message
        ad_label = StrongBodyLabel("💼 Nhận code thuê web, app, tool, game, automation\n     Liên hệ Sen.")
        ad_label.setStyleSheet("color: #FFD700; font-size: 14px;")
        ad_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(ad_label)

        layout.addStretch()

        # Close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = PrimaryPushButton(FluentIcon.ACCEPT, "OK, Bắt đầu sử dụng (3s)")
        close_btn.setFixedWidth(220)
        close_btn.setFixedHeight(36)
        close_btn.setEnabled(False)
        close_btn.clicked.connect(self.accept)
        self._close_btn = close_btn
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def _enable_close(self):
        """Cho phép đóng sau 3 giây"""
        self._can_close = True
        self._close_btn.setEnabled(True)
        self._close_btn.setText("OK, Bắt đầu sử dụng")

    def closeEvent(self, event):
        """Chặn đóng trước 3 giây"""
        if not self._can_close:
            event.ignore()
        else:
            event.accept()
