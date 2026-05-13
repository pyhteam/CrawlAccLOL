"""
Main Window - Cửa sổ chính với FluentWindow navigation
"""

import os
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from qfluentwidgets import (
    FluentWindow,
    FluentIcon,
    NavigationItemPosition,
    setTheme,
    Theme,
    setThemeColor,
    InfoBar,
    InfoBarPosition,
)

from src.ui.pages.dashboard import DashboardPage
from src.ui.pages.accounts import AccountsPage
from src.ui.pages.crawl import CrawlPage
from src.ui.pages.update_time import UpdateTimePage
from src.ui.pages.settings import SettingsPage
from src import __version__, __app_name__


class MainWindow(FluentWindow):
    """Cửa sổ chính của ứng dụng"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{__app_name__} v{__version__}")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 800)

        # Set theme
        setTheme(Theme.DARK)
        setThemeColor("#0078D4")

        # Set icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Khởi tạo các trang
        self._init_pages()
        self._init_navigation()

        # Center window
        self._center_window()

        # Hiện popup thông tin tác giả khi mở app
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(500, self._show_about_popup)

    def _show_about_popup(self):
        """Hiện popup thông tin tác giả"""
        from src.ui.dialogs.about_dialog import AboutDialog
        dialog = AboutDialog(self)
        dialog.exec_()

    def _init_pages(self):
        """Khởi tạo các trang"""
        self.dashboard_page = DashboardPage(self)
        self.accounts_page = AccountsPage(self)
        self.crawl_page = CrawlPage(self)
        self.update_time_page = UpdateTimePage(self)
        self.settings_page = SettingsPage(self)

    def _init_navigation(self):
        """Thiết lập navigation sidebar"""
        # Dashboard
        self.addSubInterface(
            self.dashboard_page,
            FluentIcon.HOME,
            "Tổng quan",
        )

        # Accounts management
        self.addSubInterface(
            self.accounts_page,
            FluentIcon.PEOPLE,
            "Tài khoản",
        )

        # Crawl
        self.addSubInterface(
            self.crawl_page,
            FluentIcon.DOWNLOAD,
            "Crawl dữ liệu",
        )

        # Update time
        self.addSubInterface(
            self.update_time_page,
            FluentIcon.STOP_WATCH,
            "Cập nhật thời gian",
        )

        # Settings (bottom)
        self.addSubInterface(
            self.settings_page,
            FluentIcon.SETTING,
            "Cài đặt",
            position=NavigationItemPosition.BOTTOM,
        )

    def _center_window(self):
        """Căn giữa cửa sổ"""
        screen = QApplication.primaryScreen()
        if screen:
            screen_geo = screen.availableGeometry()
            x = (screen_geo.width() - self.width()) // 2
            y = (screen_geo.height() - self.height()) // 2
            self.move(x, y)

    def show_info(self, title: str, content: str, info_type: str = "success"):
        """Hiển thị thông báo"""
        bar_type = {
            "success": InfoBar.success,
            "warning": InfoBar.warning,
            "error": InfoBar.error,
            "info": InfoBar.info,
        }

        func = bar_type.get(info_type, InfoBar.info)
        func(
            title,
            content,
            duration=3000,
            position=InfoBarPosition.TOP_RIGHT,
            parent=self,
        )
