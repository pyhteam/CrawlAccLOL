"""
Dashboard Page - Trang tổng quan
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
)

from qfluentwidgets import (
    ScrollArea,
    TitleLabel,
    SubtitleLabel,
    StrongBodyLabel,
    BodyLabel,
    CaptionLabel,
    CardWidget,
    IconWidget,
    FluentIcon,
)

from src.storage import AccountStorage


class StatCard(CardWidget):
    """Card thống kê"""

    def __init__(self, icon: FluentIcon, title: str, value: str, parent=None):
        super().__init__(parent)
        self.setFixedHeight(120)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        # Icon
        icon_widget = IconWidget(icon, self)
        icon_widget.setFixedSize(40, 40)
        layout.addWidget(icon_widget)

        # Text content
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

        self.title_label = CaptionLabel(title, self)
        text_layout.addWidget(self.title_label)

        self.value_label = TitleLabel(value, self)
        text_layout.addWidget(self.value_label)

        layout.addLayout(text_layout)
        layout.addStretch()

    def update_value(self, value: str):
        """Cập nhật giá trị"""
        self.value_label.setText(value)


class ShopCard(CardWidget):
    """Card thông tin shop"""

    def __init__(self, shop_name: str, count: int, parent=None):
        super().__init__(parent)
        self.setFixedHeight(72)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        # Shop info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        name_label = StrongBodyLabel(shop_name, self)
        info_layout.addWidget(name_label)

        count_label = CaptionLabel(f"{count} tài khoản", self)
        info_layout.addWidget(count_label)

        layout.addLayout(info_layout)
        layout.addStretch()

        # Count badge
        badge = TitleLabel(str(count), self)
        badge.setStyleSheet("color: #0078D4;")
        layout.addWidget(badge)


class DashboardPage(ScrollArea):
    """Trang tổng quan - Dashboard"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dashboardPage")
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
        self._init_stats()
        self._init_shops()
        self._init_price_info()

        self.main_layout.addStretch()

        # Load data
        self.refresh_data()

    def _init_header(self):
        """Header section"""
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)

        title = TitleLabel("📊 Tổng quan", self.container)
        header_layout.addWidget(title)

        subtitle = CaptionLabel(
            "Thống kê tổng hợp dữ liệu tài khoản LOL đã crawl",
            self.container,
        )
        header_layout.addWidget(subtitle)

        self.main_layout.addLayout(header_layout)

    def _init_stats(self):
        """Stat cards section"""
        stats_layout = QGridLayout()
        stats_layout.setSpacing(12)

        self.total_card = StatCard(
            FluentIcon.PEOPLE, "Tổng tài khoản", "0", parent=self.container
        )
        stats_layout.addWidget(self.total_card, 0, 0)

        self.shops_card = StatCard(
            FluentIcon.SHOPPING_CART, "Số shop", "0", parent=self.container
        )
        stats_layout.addWidget(self.shops_card, 0, 1)

        self.price_min_card = StatCard(
            FluentIcon.REMOVE_FROM, "Giá thấp nhất", "0 VNĐ", parent=self.container
        )
        stats_layout.addWidget(self.price_min_card, 0, 2)

        self.price_max_card = StatCard(
            FluentIcon.ADD_TO, "Giá cao nhất", "0 VNĐ", parent=self.container
        )
        stats_layout.addWidget(self.price_max_card, 0, 3)

        self.main_layout.addLayout(stats_layout)

    def _init_shops(self):
        """Shop breakdown section"""
        section_label = SubtitleLabel("Phân bố theo Shop", self.container)
        self.main_layout.addWidget(section_label)

        self.shops_layout = QVBoxLayout()
        self.shops_layout.setSpacing(8)
        self.main_layout.addLayout(self.shops_layout)

    def _init_price_info(self):
        """Price info section"""
        section_label = SubtitleLabel("Thống kê giá", self.container)
        self.main_layout.addWidget(section_label)

        self.price_card = CardWidget(self.container)
        price_layout = QHBoxLayout(self.price_card)
        price_layout.setContentsMargins(20, 16, 20, 16)

        self.price_avg_label = BodyLabel("Giá trung bình: --", self.price_card)
        price_layout.addWidget(self.price_avg_label)
        price_layout.addStretch()

        self.main_layout.addWidget(self.price_card)

    def refresh_data(self):
        """Refresh dữ liệu thống kê"""
        storage = AccountStorage()
        summary = storage.export_summary()

        total = summary.get("total", 0)
        shops = summary.get("shops", {})
        price_min = summary.get("price_min", 0)
        price_max = summary.get("price_max", 0)
        price_avg = summary.get("price_avg", 0)

        # Update stat cards
        self.total_card.update_value(f"{total:,}")
        self.shops_card.update_value(str(len(shops)))
        self.price_min_card.update_value(f"{price_min:,} VNĐ")
        self.price_max_card.update_value(f"{price_max:,} VNĐ")

        # Update price avg
        self.price_avg_label.setText(f"Giá trung bình: {price_avg:,} VNĐ")

        # Update shop cards
        # Clear existing
        while self.shops_layout.count():
            item = self.shops_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for shop_name, count in shops.items():
            card = ShopCard(shop_name, count, self.container)
            self.shops_layout.addWidget(card)
